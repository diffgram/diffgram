const [data, error] = await get_model_run_list('12345', [1, 2, 3]);
if (data) {
  // handle successful response
} else if (error) {
  // handle error
}
