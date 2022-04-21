def add_arrows_to_string_func(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    index_start = max(text.rfind('\n', 0, pos_start.index), 0)
    index_end = text.find('\n', index_start + 1)
    if index_end < 0: index_end = len(text)
    
    # Generate each line
    line_count = pos_end.lineNum - pos_start.lineNum + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[index_start:index_end]
        colNum_start = pos_start.colNum if i == 0 else 0
        colNum_end = pos_end.colNum if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * colNum_start + '^' * (colNum_end - colNum_start)

        # Re-calculate indices
        index_start = index_end
        index_end = text.find('\n', index_start + 1)
        if index_end < 0: index_end = len(text)

    return result.replace('\t', '')