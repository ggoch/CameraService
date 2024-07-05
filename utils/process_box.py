def box_is_inside(box1, box2):
    """
    判斷矩形 box1 是否完全在矩形 box2 內部。

    box1 和 box2 是字典對象，包含 x1, y1, x2, y2 四個鍵。
    """
    return (box1['x1'] >= box2['x1'] and
            box1['y1'] >= box2['y1'] and
            box1['x2'] <= box2['x2'] and
            box1['y2'] <= box2['y2'])