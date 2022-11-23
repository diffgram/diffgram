interface TextCoordinates {
    x: number;
    y: number;
}

interface Line {
    id: number;
    y: number
}

interface Token {
    id: number;
    line: number;
    start_x: number;
    width: number;
}

const line_search = (lines: Array<Line>, y: number): Line => {
    const start_line: Line = lines.filter(line => line.y <= y).pop();
    const finish_line: Line = lines.find(line => line.y >= y);

    if (!start_line) return finish_line;
    if (!finish_line) return start_line;

    const prev_delta: number = start_line.y - y;
    const next_delta: number = finish_line.y - y;

    return Math.abs(prev_delta) > Math.abs(next_delta) ? finish_line : start_line
}

const token_search = (tokens: Array<Token>, x: number): Token => {
    const is_first_token = tokens[0].start_x > x
    if (is_first_token) return tokens[0]

    const token: Token = tokens.find(token => token.start_x < x && token.start_x + token.width > x)
    if (token) return token

    const prev_token = tokens.filter(token => token.start_x + token.width < x).pop()
    return prev_token
}

export default function(token_list: Array<Token>, line_list: Array<Line>, coordinates: TextCoordinates): Token {
    const max_line_id = line_list[line_list.length - 1].id
    const new_line: Line = line_search(line_list, coordinates.y)
    let line_tokens: Token[] = [];
    let line_id = new_line.id

    while (line_tokens.length === 0) {
        if (line_id > max_line_id) break

        line_tokens = token_list.filter(token => token.line === line_id)
        if (line_tokens.length === 0) line_id += 1
    }
    
    const token_to_return = token_search(line_tokens, coordinates.x)
    return token_to_return
}