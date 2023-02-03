

export class PanelsSettings {
  rows: number

  columns: number

  constructor(rows: number, columns: number) {
    this.rows = rows
    this.columns = columns
  }

  public set_cols_and_rows_from_total_items(cols, item_nums){
    let rows = Math.ceil(item_nums / cols)
    this.rows = rows
    this.columns = cols
  }
}
