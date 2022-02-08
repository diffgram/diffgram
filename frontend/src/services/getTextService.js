import axios from "axios"

export default async (url_signed) => {
    try {
        console.log('get test', url_signed)
        const { data:text } = await axios.get(url_signed)
        return text
    } catch {
        return ''
    }
}
