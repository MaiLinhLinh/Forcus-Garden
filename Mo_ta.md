# 1 Tổng quan dự án
## 1.1. Tổng quan dự án
Focus Garden là một nền tảng hỗ trợ sinh viên duy trì thói quen học tập tập trung thông qua cơ chế xây dựng và phát triển không gian xanh ảo gắn với quá trình học tập hằng ngày.
Khác với các công cụ chỉ tập trung vào đếm thời gian hoặc chặn xao nhãng, Focus Garden hướng tới việc duy trì nhịp học bền vững bằng một trải nghiệm gần giống game, trong đó người dùng không bị “giám sát” hay ép buộc, mà được khuyến khích quay lại học đều mỗi ngày thông qua các phản hồi trực quan và cảm giác đồng hành.
Hệ thống tạo động lực cho người học bằng cách kết hợp:
+ phiên học có mục tiêu rõ ràng (do người dùng tự đặt mục tiêu về thời lượng học bài)
+ Study Zone giúp theo dõi học tập theo ngữ cảnh nhiều tab, nhiều ứng dụng
+ cây đồng hành xuất hiện trong suốt phiên học
## 1.2. Bài toán mà dự án giải quyết
Nhiều sinh viên học online hoặc tự học trên máy tính gặp tình trạng:
ngồi học lâu nhưng hiệu quả thấp
dễ bị phân tán bởi mạng xã hội, tab khác, ứng dụng khác
khó duy trì thói quen học đều mỗi ngày
thiếu động lực để quay lại học sau vài hôm đứt nhịp
các công cụ hiện tại thiên về quản lý thời gian hơn là duy trì hành vi
## 1.3. Cơ chế theo dõi nhiều tab trong phiên học
Nếu người dùng cần mở nhiều tab hoặc nhiều ứng dụng để học, hệ thống không coi việc chuyển tab là mất tập trung ngay lập tức.
Thay vào đó, trước khi bắt đầu phiên học, người dùng sẽ khai báo một nhóm tab hoặc ứng dụng liên quan đến buổi học, gọi là study zone. Ví dụ:
+ Google Docs
+ PDF bài giảng
+ YouTube bài học
+ VS Code
+ Stack Overflow
+ ....
Trong suốt phiên học, hệ thống sẽ kiểm tra xem người dùng có còn hoạt động trong nhóm này hay không.
# 2 Chức năng
# 2.1. Chức năng tạo tài khoản và hồ sơ cá nhân
Ứng dụng cho phép người dùng đăng ký và đăng nhập bằng email, tài khoản Google hoặc các phương thức liên kết khác. Sau khi tạo tài khoản, người dùng có thể thiết lập hồ sơ cá nhân gồm tên hiển thị, ảnh đại diện, mục tiêu học tập.
Hồ sơ cá nhân là nơi lưu toàn bộ tiến trình của người dùng, bao gồm:
+ số phiên học đã hoàn thành
+ Các thông tin liên quan
# 2.2. Chức năng bắt đầu phiên học
Trước mỗi buổi học, người dùng có thể tạo một phiên học mới. Ở bước này, ứng dụng cho phép khai báo:
+ tên môn học hoặc chủ đề đang học
+ thời lượng dự kiến
+ nhóm tab hoặc ứng dụng liên quan đến buổi học
Khi phiên học bắt đầu, hệ thống sẽ kích hoạt cây đồng hành và ghi nhận toàn bộ hoạt động liên quan đến phiên đó.
Đây là chức năng rất quan trọng vì nó giúp biến một hành động mơ hồ như “ngồi vào bàn học” thành một phiên học rõ ràng, có mục tiêu và có tiến trình
# 2.3. Chức năng Study Zone
Study Zone là chức năng cho phép người dùng khai báo trước những tab, website hoặc ứng dụng được xem là hợp lệ trong một phiên học.
Ví dụ người dùng có thể chọn:
+ Google Docs
+ PDF giáo trình
+ VS Code
+ YouTube bài giảng
+ Stack Overflow
+ Notion
+ ...
Trong quá trình học, ứng dụng không ép người dùng phải ở yên một tab duy nhất. Thay vào đó, hệ thống chỉ kiểm tra xem người dùng có còn hoạt động trong nhóm tài nguyên đã khai báo hay không.
+ Nếu người dùng chuyển đổi giữa các tab hoặc ứng dụng thuộc Study Zone, hệ thống vẫn xem đó là hành vi học tập bình thường.
+ Nếu người dùng rời khỏi Study Zone quá lâu hoặc quá nhiều lần, hoặc không tương tác màn hình trong một khoảng thời gian bao lâu đó, ... hoặc vi phạm 1 số rule cơ bản được quy vào việc xao nhãng, hệ thống mới ghi nhận dấu hiệu lệch nhịp.
Chức năng này giúp sản phẩm phù hợp hơn với hành vi học thật, vì sinh viên thường phải mở nhiều tab cùng lúc để học.
# 2.4. Chức năng cây đồng hành nổi trên màn hình
Trong suốt phiên học, một cây đồng hành nhỏ sẽ xuất hiện cố định ở góc màn hình dưới dạng widget nổi. Cây này luôn hiện diện xuyên suốt, kể cả khi người dùng đổi tab hay đổi ứng dụng trong phạm vi phiên học.
Cây đồng hành có các vai trò:
+ phản ánh trạng thái hiện tại của phiên học
+ tạo cảm giác có một “sinh vật sống” đang học cùng người dùng
+ Hiển thị đồng hồ đếm ngược thời gian học
Widget cây có thể:
+ thu gọn
+ di chuyển vị trí
# 2.5. Màn hình tổng kết sau phiên học
Bắt buộc phải có màn hình tổng kết sau mỗi phiên để hiển thị:
phiên học có hợp lệ hay không, số lần xao nhãng, thời gian vi phạm, ....
Màn hình này rất quan trọng để nối toàn bộ vòng lặp sản phẩm thành một trải nghiệm hoàn chỉnh.

