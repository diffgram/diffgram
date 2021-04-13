
function format_money(value) {
  return '$' + (value / 100).toLocaleString('en-US', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2
  })
}
