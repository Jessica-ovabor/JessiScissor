
// Function to close the alert
function closeAlert(element) {
    element.parentElement.remove();
}
//function for preloaser

    var loadingOverlay = document.getElementById('preloader');
    window.addEventListener('load', function() {
    loadingOverlay.style.display='none';
  });
function myFunction(){
    var copyText= document.getElementById("myInput")
    copyText.select()
    copyText.setSelectRange(0,99999)
    navigator.clipboard.writeText(copyText.value)
    alert("URL copied: " + copyText.value)

}

  