# OPENCORE - ADD
# For database classes
# search tags:  CACHE 
import datetime


class Caching(object):
    """
    For a mixin
     ie class File(Base, Caching):

    Assumes child class defines a
    cache_dict = Column(MutableDict.as_mutable(JSONEncodedDict),
                    default = {})
    """

    def get_with_cache(self,
                       cache_key: str,
                       cache_miss_function,
                       session,
                       miss_function_args={}):
        """
        Abstract implementation.

        Return cache if exists otherwise use function to get

        Assumes to add to session if Miss.
        Session may not exist. In which case we assume
            it's still better to run the cache_miss_function
            for example for a new project.

        We pass cach_key to regenerate_cache_by_key so that it automatically
        will match. That way a user needs only use this function, and the
        cache_miss_function that's passed doesn't have ot know about the caching
        concepts.


        Cache Info __info concept:
            Why: For debugging good to know.
            Also could use it if cache is getting too stale. (eg by default we refresh if too
            old even if no direct trigger).

        Composite key idea
            Context: The datatype is unknown and don't want to start recursively
            sniffing the data type...
            eg could be list of dicts or list of ints, or single int, etc.

        Separate dict because:
        __info name because 'info' seems too high level may want to use that for normal use
        dictionary
        
        a) We can serialize single __info even if multiple attributes (vs having to declare key each time)
        b) Can add date generated (which is separate from bool)

        Example of how to get cache info
            Add this key on the return object: 
                'cache_info': self.cache_dict.get('__info') if self.cache_dict else None
            See project.py for example
            Careful, cache_dict could be None

        Example of the output it shows:
            project: {
                cache_info: {
                    directory_list: {
                        from_cache: false, 
                        regenerate_datetime: "2020-09-21T23:59:05.819037"}
                    member_list: {
                        from_cache: true
                    }
                    preview_file_list: {
                        from_cache: true
                    }

        Slight gotcha:
            If the return dictionary has ints (eg for frame) then it doesn't like
            a string like 'cache_info'.
            Alternative here is to include it in response level 

        TODO 
            Freshness:
                Wanting to apply some form of default freshness, 
                eg so we always refresh after some period even if no 'known' change
        """

        # Null case
        if self.cache_dict is None:
            self.cache_dict = {}

        if self.cache_dict.get('__info') is None:
            self.cache_dict['__info'] = {}

        if self.cache_dict['__info'].get(cache_key) is None:
            self.cache_dict['__info'][cache_key] = {} 

        # Cache hit
        existing = self.cache_dict.get(cache_key)

        if existing is not None:
            self.cache_dict['__info'][cache_key]['from_cache'] = True
            return existing

        # Miss
        else:
            self.cache_dict['__info'][cache_key]['from_cache'] = False
            if session:
                session.add(self)
            return self.regenerate_cache_by_key(
                cache_key=cache_key,
                regenerate_function=cache_miss_function,
                miss_function_args=miss_function_args
            )


    def clear_cache(self):
        self.cache_dict = {}


    def set_cache_by_key(
            self,
            cache_key: str,
            value=None):

        if self.cache_dict is None:
            self.cache_dict = {}

        self.cache_dict[cache_key] = value


    def set_cache_key_dirty(
            self,
            cache_key: str
    ):
        # Does not add to session.
        if self.cache_dict:
            self.cache_dict[cache_key] = None


    def regenerate_cache_by_key(self,
                                cache_key: str,
                                regenerate_function,
                                miss_function_args={}):
        # This assumes that get_with_cache() has been called first

        self.cache_dict[cache_key] = regenerate_function(**miss_function_args)
        self.cache_dict['__info'][cache_key]['regenerate_datetime'] = datetime.datetime.utcnow().isoformat()
        return self.cache_dict[cache_key]
