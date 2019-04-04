var initialImage = "";



function uploadFile(){
  // jQuery doesn't really help me with file inputs, so I have to do it with DOM selector
  fileInput = document.getElementById("pictureUploadInput");
  imageDisplay = $("#userImage");
  fullForm = $('#ajaxForm :input[id!=pictureUploadInput]');
  if(fileInput.value){
    file = fileInput.files[0];
    // File is now available for the upload
    formData = new FormData();
    formData.append('file', file);

    $.ajax({
      url:"processImage",
      type:"post",
      data:formData,
      contentType: false,
      processData: false,
      success:uploadFileCallback
    });
  } else {
    alert("Please select an image to use");
  }
}
function uploadFileCallback(data,status){
  console.log(data);
}
