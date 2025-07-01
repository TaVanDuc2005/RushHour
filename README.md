# RushHour

pip install pygame
pip install opencv-python

images:
A,B,C car is horizontal
D,E,F car is not horizontal

Hình dạng xe
Mỗi xe phải thoả mãn:
✅ Tất cả các ô của xe nằm liên tiếp cùng hàng (ngang) hoặc cùng cột (dọc).
Không được để xe hình chữ L.

❌ Sai ví dụ:
..A...
A.....
vì A không thẳng hàng.

✅ Đúng ví dụ:
..A...
..A...

🟥 đỏ phải nằm ngang
Luôn nằm ngang, vì mục tiêu là đẩy xe đỏ ra phía bên phải map.

Xe đỏ không được dọc, ví dụ:
......
..R...
..R...

là sai.

Ví dụ đúng:
..RR..

🛑 Xe không trùng nhau
Không có 2 xe chồng lên cùng 1 ô.

Mỗi ô chỉ thuộc 1 xe duy nhất.

🚪 Cửa ra xe đỏ
Thường quy định xe đỏ thoát ra bên phải dòng thứ 3 (dòng index 2).

Ví dụ:
RR....
thì R nằm trên dòng 2 (dòng thứ 3).

🧮 Tối thiểu số ô xe
Mỗi xe phải có ít nhất 2 ô liên tiếp.

Không được khai báo xe chỉ chiếm 1 ô (sẽ lỗi).

Ví dụ:
A.....
sai, vì A chỉ có 1 ô.

