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

    return prev_delta > next_delta ? finish_line : start_line
}

const token_search = (tokens: Array<Token>, x: number): Token => {
    const token: Token = tokens.find(token => token.start_x < x && token.start_x + token.width > x)
    if (token) return token

    const prev_token = tokens.filter(token => token.start_x + token.width < x).pop()
    return prev_token
}

export default function(token_list: Array<Token>, line_list: Array<Line>, coordinates: TextCoordinates): Token {
    const new_line: Line = line_search(line_list, coordinates.y)
    const line_tokens: Array<Token> = token_list.filter(token => token.line === new_line.id)
    const token_to_return = token_search(line_tokens, coordinates.x)
    return token_to_return
}