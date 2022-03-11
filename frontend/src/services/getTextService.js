import axios from './customInstance'

export default async (url_signed) => {
    try {
        const { data:text } = await axios.get(url_signed)
        return text
    } catch {
        return ''
    }
}
