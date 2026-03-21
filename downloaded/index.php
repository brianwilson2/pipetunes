<?php
// Absolute path to your pipetunes folder
$dir = $_SERVER['DOCUMENT_ROOT'] . '/pipetunes';

// Check folder exists
if (!is_dir($dir)) {
    echo "<p style='color:red;'>Folder not found: $dir</p>";
    $files = [];
} else {
    $files = array_diff(scandir($dir), array('.', '..'));
    sort($files);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Digital Tune Book</title>
<style>
  body { font-family: sans-serif; padding: 20px; }
  #search { width: 100%; padding: 8px; margin-bottom: 10px; font-size: 16px; }
  .category-btn { padding: 6px 12px; margin: 2px; cursor: pointer; background: #eee; border: 1px solid #ccc; border-radius: 4px; }
  .category-btn.active { background: #0066cc; color: white; }
  ul { list-style: none; padding: 0; }
  li { margin: 5px 0; }
  a { text-decoration: none; color: #0066cc; }
  a:hover { text-decoration: underline; }

  /* New class for all tune items */
  .tune-item {
      font-size: 18px;       /* base font size */
      line-height: 1.4;      /* spacing */
      white-space: normal;   /* wrap long names */
  }

  /* Optional: scale font slightly on very small screens */
  @media (max-width: 400px) {
      .tune-item {
          font-size: 16px;
      }
  }
</style>
</head>
<body>

<h2>Digital Tune Book</h2>

<div id="categories">
  <button class="category-btn" data-cat="all">All</button>
  <button class="category-btn" data-cat="jig">Jig</button>
  <button class="category-btn" data-cat="reel">Reel</button>
  <button class="category-btn" data-cat="march">March</button>
  <button class="category-btn" data-cat="hornpipe">Hornpipe</button>
  <button class="category-btn" data-cat="strath">Strathspey</button>
  <button class="category-btn" data-cat="retreat">Retreat</button>
  <button class="category-btn" data-cat="lament">Lament</button>
  <button class="category-btn" data-cat="slowair">Slow Air</button>
</div>

<input type="text" id="search" placeholder="Search tunes...">

<ul id="fileList">
<?php
foreach ($files as $file) {
    if (strtolower(pathinfo($file, PATHINFO_EXTENSION)) !== 'pdf') continue;
    $filename = pathinfo($file, PATHINFO_FILENAME);

    // Detect category from prefix
    if (preg_match('/^(jig|reel|march|hornpipe|strath|retreat|lament|slowair)[-_]/i', $filename, $matches)) {
        $cat = strtolower($matches[1]);
    } else {
        $cat = 'other';
    }

    // Display name without prefix
    $display = preg_replace('/^(hornpipe|march|strath|reel|retreat|jig|lament|slowair)[-_]/i', '', $filename);

    // Add class "tune-item" to each li
    echo "<li class='tune-item' data-cat='$cat'><a href='viewer.php?file=$file'>$display</a></li>\n";
}
?>
</ul>

<script>
const searchInput = document.getElementById('search');
const fileList = document.getElementById('fileList');
const categoryButtons = document.querySelectorAll('.category-btn');

let activeCategory = 'all';

function filterList() {
  const filter = searchInput.value.toLowerCase();
  Array.from(fileList.getElementsByTagName('li')).forEach(li => {
    const matchesSearch = li.textContent.toLowerCase().includes(filter);
    const matchesCategory = (activeCategory === 'all') || (li.dataset.cat === activeCategory);
    li.style.display = (matchesSearch && matchesCategory) ? '' : 'none';
  });
}

// Live search
searchInput.addEventListener('input', filterList);

// Category buttons
categoryButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    categoryButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeCategory = btn.dataset.cat;
    filterList();
  });
});

// Set "All" as default active
document.querySelector('.category-btn[data-cat="all"]').classList.add('active');
</script>

</body>
</html>