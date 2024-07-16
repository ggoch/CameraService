import math

def box_is_inside(box1, box2):
    """
    判斷矩形 box1 是否完全在矩形 box2 內部。

    box1 和 box2 是字典對象，包含 x1, y1, x2, y2 四個鍵。
    """
    return (box1['x1'] >= box2['x1'] and
            box1['y1'] >= box2['y1'] and
            box1['x2'] <= box2['x2'] and
            box1['y2'] <= box2['y2'])

def remove_duplicate_boxes(detected_boxes):
        # 使用集合来存储唯一的坐标元组
        seen_coordinates = set()
        unique_boxes = []
    
        for box in detected_boxes:
            # 将坐标数组转换为不可变的元组
            coordinates_tuple = tuple([box[0], box[1], box[2], box[3]])
            
            # 检查元组是否已经在集合中
            if coordinates_tuple not in seen_coordinates:
                seen_coordinates.add(coordinates_tuple)
                unique_boxes.append(box)
        
        return unique_boxes

def calculate_distance(box1, box2):
    # 计算两个盒子中心点之间的欧几里得距离
    x1, y1, w1, h1 = box1[:4]
    x2, y2, w2, h2 = box2[:4]
    center1 = (x1 + w1 / 2, y1 + h1 / 2)
    center2 = (x2 + w2 / 2, y2 + h2 / 2)
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

def remove_close_boxes(detected_boxes, threshold):
    filtered_boxes = []
    
    for box in detected_boxes:
        too_close = False
        for filtered_box in filtered_boxes:
            if calculate_distance(box, filtered_box) < threshold:
                too_close = True
                break
        if not too_close:
            filtered_boxes.append(box)
    
    return filtered_boxes

def splice_by_label(lst, label_to_remove):
    removed_item = None
    for i, item in enumerate(lst):
        if item[4] == label_to_remove:
            removed_item = lst.pop(i)
            break
    return removed_item