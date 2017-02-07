import traceback

def load_csv_file(file, read_cols = None, spliter = ',', offset = 0, size = 100):
  line = None
  single_col_idx = read_cols and len(read_cols) == 1 and read_cols[0]
  result = []
  cursor = -1
  with open(file) as f:
    while True:
      line = f.readline()
      if line:
        try: 
          cursor += 1
          if cursor < offset:
            continue
          if cursor > offset + size:
            break
          row = line.replace('\n', '').split(spliter)
          if single_col_idx != None:
            row = row[single_col_idx]
          elif read_cols:
            row = [row[i] for i in read_cols]
          result.append(row)
        except Exception as e:
          print('error loading file, line: %s' % line, e)
          traceback.print_exc()
      else:
        break
  return result

if __name__ == '__main__':
  print(load_csv_file('/Users/vansteve911/Desktop/distinct_colleges.csv', [0], offset = 200, size = 10))
