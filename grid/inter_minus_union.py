

def get_precedent_zone(last_box, current_box):
        # determine the (x, y)-coordinates of the intersection rectangle


        x_a = max(last_box[0], current_box[0])
        y_a = max(last_box[1], current_box[1])
        x_b = min(last_box[2], current_box[2])
        y_b = min(last_box[3], current_box[3])

        #position down
        if bbox1[0] == bbox2[0]:
                return [last_box[0], last_box[1], last_box[2], current_box[1]]

        #position right
        elif bbox1[1] == bbox2[1]:
                return [last_box[0], last_box[1], current_box[0], last_box[3]]


if __name__ == "__main__":
        bbox1 = [0, 150, 50, 200]
        bbox2 = [5, 150, 55, 200]
        print(get_precedent_zone(last_box=bbox1, current_box=bbox2))

