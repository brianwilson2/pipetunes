<?php
// Get current file
$file = basename($_GET['file']); 

// Folder with all PDFs
$dir = __DIR__;  // same folder as viewer.php

// Build list of PDFs in order
$all_files = array_values(array_filter(scandir($dir), function($f){
    return strtolower(pathinfo($f, PATHINFO_EXTENSION)) === 'pdf';
}));

// Find current index
$current_index = array_search($file, $all_files);
?>
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { margin:0; font-family:Arial; }
.topbar{
    background:#333; color:white; padding:10px; display:flex; justify-content:space-between; align-items:center;
}
.back, .nav{
    color:white; text-decoration:none; font-weight:bold; padding:0 10px;
    cursor:pointer;
}
iframe{ width:100%; height:95vh; border:none; }
</style>
</head>
<body>

<div class="topbar">
<a class="back" href="index.php">← Back</a>
<div>
  <span class="nav" id="prev">◀ Prev</span>
  <span class="nav" id="next">Next ▶</span>
</div>
</div>

<iframe id="pdfFrame" src="<?php echo $file; ?>"></iframe>

<script>
let files = <?php echo json_encode($all_files); ?>;
let index = <?php echo $current_index; ?>;

const iframe = document.getElementById('pdfFrame');

function goTo(i){
    if(i < 0) i = 0;
    if(i >= files.length) i = files.length -1;
    index = i;
    iframe.src = files[index];
}

// Arrow keys navigation
document.addEventListener('keydown', e => {
    if(e.key === 'ArrowLeft') goTo(index-1);
    if(e.key === 'ArrowRight') goTo(index+1);
});

// Buttons
document.getElementById('prev').addEventListener('click', () => goTo(index-1));
document.getElementById('next').addEventListener('click', () => goTo(index+1));

// Swipe navigation
let touchstartX = 0;
let touchendX = 0;

function handleGesture() {
    if(touchendX < touchstartX - 50) goTo(index+1); // swipe left → next
    if(touchendX > touchstartX + 50) goTo(index-1); // swipe right → prev
}

document.addEventListener('touchstart', e => { touchstartX = e.changedTouches[0].screenX; });
document.addEventListener('touchend', e => { 
    touchendX = e.changedTouches[0].screenX; 
    handleGesture();
});
</script>

</body>
</html>