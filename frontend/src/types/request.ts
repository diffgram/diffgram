export type RequestResponse<T> = {
    result: T | null
    error: Error | null
}