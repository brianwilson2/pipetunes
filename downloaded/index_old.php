<?php
// CONFIG: categories and filename prefixes
$categories = [
    'Jigs' => 'jig_',
    'Reels' => 'reel_',
    'Marches' => 'march_',
    'Strathspeys' => 'strathspey_'
];

// Scan folder for PDFs
$allFiles = glob("*.pdf");
sort($allFiles);

// Organize files by category
$filesByCategory = [];
foreach ($categories as $cat => $prefix) {
    $filesByCategory[$cat] = array_filter($allFiles, function($f) use ($prefix) {
        return stripos($f, $prefix) === 0;
    });
}

// Uncategorized PDFs
$uncat = array_filter($allFiles, function($f) use ($categories) {
    foreach ($categories as $prefix) {
        if (stripos($f, $prefix) === 0) return false;
    }
    return true;
});
if ($uncat) $filesByCategory['Other Tunes'] = $uncat;
?>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pipe Tune Book</title>
<link rel="icon" href="icon.png">
<meta name="theme-color" content="#2d6cdf">

<style>
body { font-family: Arial, sans-serif; margin:20px; background:#f4f4f4; }
h1 { text-align:center; }
h2 { margin-top:30px; color:#333; }
#search { width:100%; padding:10px; font-size:16px; margin-bottom:20px; }

.tune {
    display:block;
    background:#2d6cdf;
    color:white;
    text-decoration:none;
    padding:12px;
    margin:8px auto;
    border-radius:6px;
    max-width:600px;   /* prevents stretching on desktop */
    text-align:center;
}

.tune:hover { background:#1f4fa3; }

#viewer {
    display:none;
    position:fixed;
    top:0; left:0;
    width:100%; height:100%;
    background:white;
    z-index:9999;
}

#viewer iframe {
    width:100%; height:100%; border:none;
}

#closeBtn {
    position:absolute; top:10px; right:10px;
    background:#2d6cdf; color:white; border:none;
    padding:10px 15px; border-radius:5px; font-size:16px;
    z-index:10000; cursor:pointer;
}
#closeBtn:hover { background:#1f4fa3; }

</style>

<script>
function searchTunes() {
    let input = document.getElementById("search").value.toLowerCase();
    let tunes = document.getElementsByClassName("tune");
    for (let i=0; i<tunes.length; i++) {
        let text = tunes[i].innerText.toLowerCase();
        tunes[i].style.display = text.includes(input) ? "block" : "none";
    }
}

function openPDF(url) {
    document.getElementById('pdfFrame').src = url;
    document.getElementById('viewer').style.display = 'block';
}

function closeViewer() {
    document.getElementById('viewer').style.display = 'none';
    document.getElementById('pdfFrame').src = '';
}
</script>
</head>

<body>

<h1>Pipe Tune Book</h1>
<input type="text" id="search" onkeyup="searchTunes()" placeholder="Search tunes...">

<?php foreach ($filesByCategory as $category => $files): ?>
    <h2><?= $category ?></h2>
    <?php foreach ($files as $file): 
        $name = ucwords(str_replace("_"," ",basename($file, ".pdf"))); ?>
        <a class="tune" href="javascript:void(0);" onclick="openPDF('<?= $file ?>')"><?= $name ?></a>
    <?php endforeach; ?>
<?php endforeach; ?>

<!-- Full-screen PDF viewer -->
<div id="viewer">
    <button id="closeBtn" onclick="closeViewer()">Back</button>
    <iframe id="pdfFrame"></iframe>
</div>

</body>
</html>