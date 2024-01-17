function checkImageProcessingStatus() {
    $.ajax({
        url: 'http://localhost:5000/checkStatus',
        type: 'GET',
        success: function(response) {
            if (response.status) {
                console.log("Ảnh đã được xử lý. Đang lấy ảnh...");

                // Lấy ảnh đã xử lý
                $.ajax({
                    url: "http://localhost:5000/getProcessedImages",
                    type: "GET",
                    success: function(data) {
                        console.log("Đã nhận được ảnh đã xử lý:", data);
                        
                        displayProcessedImages(data.images);
                    },
                    error: function (error) {
                        console.log("Lỗi khi lấy thông tin ảnh đã xử lý:", error);
                    }
                });

            } else {
                console.log("Ảnh chưa được xử lý.");
                setTimeout(checkImageProcessingStatus, 2000); // Polling sau mỗi 2 giây
            }
        },
        error: function(error) {
            console.log("Lỗi khi kiểm tra trạng thái xử lý ảnh:", error);
        }
    });
}

function getIdTimeInfo() {
    $.ajax({
        url: 'http://localhost:5000/getIdTimeInfo',
        type: 'GET',
        success: function(data) {
            console.log("Thông tin ID và Thời gian nhận được:", data);
            if(data.ID && data.time) {
                displayIDAndTime(data);
            } else {
                console.log("Không có thông tin ID và Thời gian.");
            }
        },
        error: function(error) {
            console.log("Lỗi khi lấy thông tin ID và Thời gian:", error);
        }
    });
}

function displayProcessedImages(images) {
    for (let i = 0; i < images.length; i++) {
        const imageBase64 = images[i];
        const imageElement = $('<img>', {
            src: 'data:image/jpeg;base64,' + imageBase64,
            class: 'processed-image'
        });
        $('#image-box-' + (i + 1)).empty().append(imageElement);
    }
}

window.onload = () => {
    checkImageProcessingStatus();
    getIdTimeInfo();
    $('#logbutton').click(() => {
    var host = window.location.hostname;
    var port = ":5000"; // Cổng của ứng dụng web
    var path = "/history"; // Đường dẫn mà bạn muốn truy cập

    // Tạo URL đầy đủ
    var fullUrl = "http://" + host + port + path;

    // Redirect sang URL mới
    window.open(fullUrl, "_blank");
    });
    
};
function displayIDAndTime(data) {
	// Assuming the data from the server includes 'ID' and 'time' fields
	let ID = data['ID'];
	let time = data['time'];
    console.log(ID);
    console.log(time);
	// Display ID and time in your HTML or update any specific elements
	$('#ID').text(ID);
	$('#time').text(time);
  }
  function readUrl(input, imageBoxNumber) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            // Tạo và cập nhật hình ảnh
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.height = '150px';  // Thiết lập kích thước hình ảnh
            img.style.width = '200px';

            // Lấy phần tử để hiển thị hình ảnh và thêm hình ảnh vào đó
            const imageBox = document.getElementById(`preview-image-box-${imageBoxNumber}`);
            imageBox.innerHTML = ''; // Xóa nội dung hiện tại (nếu có)
            imageBox.appendChild(img);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

//=============================

