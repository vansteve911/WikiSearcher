import traceback

def load_csv_file(file, read_cols = None, offset = 0, size = 100):
  line = None
  single_col_idx = read_cols and len(read_cols) == 1 and read_cols[0]
  try:
    result = []
    cursor = -1
    with open(file) as f:
      while True:
        cursor += 1
        if cursor < offset:
          continue
        if cursor > offset + size:
          break
        line = f.readline()
        if line:
          row = line.replace('\n', '').split(',')
          if single_col_idx != None:
            row = row[single_col_idx]
          elif read_cols:
            row = [row[i] for i in read_cols]
          result.append(row)
        else:
          break
    return result
  except Exception as e:
    print('error loading file, line: %s' % line, e)
    traceback.print_exc()

if __name__ == '__main__':
  print(load_csv_file('/Users/vansteve911/Desktop/distinct_colleges.csv', [0], offset = 100, size = 10))
