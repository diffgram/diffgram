import axios from 'axios'

export const is_mailgun_set = async () => {
    try {
        const { data } = await axios.get('/api/configs/is-mailer-set')
        return data
    } catch(e) {
        return {
            mailgun: false
        }
    }
}