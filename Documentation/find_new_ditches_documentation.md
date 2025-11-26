<h1>Find New Ditches</h1>
<p>This script identifies new ditch segments by comparing new and old raster probability maps.</p>
<h2>Overview</h2>
<p>The <code>find_new_ditches.py</code> script processes raster files to identify new ditch segments that are present in the new raster layers but absent in the old ones. The script merges raster tiles, performs reprojection, identifies differences, converts rasters to vectors, and filters overlapping features.</p>
<h2>Features</h2>
<ol>
<li><strong>Merge Raster Tiles</strong>: Combines raster tiles for new and old layers.</li>
<li><strong>Reprojection</strong>: Aligns old raster to match the new raster for comparison.</li>
<li><strong>Difference Calculation</strong>: Identifies new ditch segments based on a specified probability threshold.</li>
<li><strong>Raster to Vector Conversion</strong>: Converts the identified ditch segments from raster format to vector format.</li>
<li><strong>Overlap Removal</strong>: Filters features that overlap with old ditch segments using a specified buffer distance.</li>
</ol>
<h2>Installation</h2>
<p>Ensure you have the required Python packages installed:</p>
<div class="code-block-parent">
<div class="code-block-container">
<button aria-label="Copy code" class="copy-code-button"><i aria-hidden="true" class="aalto-icon aalto-icon--copy"></i></button>
<pre style="overflow-x: auto;"><code class="language-bash">pip install rasterio numpy geopandas scipy shapely
</code></pre>
</div>
</div>
<h2>Usage</h2>
<p>Run the script using the command line interface:</p>
<div class="code-block-parent">
<div class="code-block-container">
<button aria-label="Copy code" class="copy-code-button"><i aria-hidden="true" class="aalto-icon aalto-icon--copy"></i></button>
<pre style="overflow-x: auto;"><code class="language-bash">python find_new_ditches.py &lt;new_layer_path&gt; &lt;old_layer_path&gt; &lt;output_dir&gt;
</code></pre>
</div>
</div>
<h3>Arguments</h3>
<ul>
<li><code>new_layer</code>: Path to new ditch probability raster directory containing <code>.tif</code> tiles.</li>
<li><code>old_layer</code>: Path to old ditch probability raster directory containing <code>.tif</code> tiles.</li>
<li><code>output_dir</code>: Directory where output files will be saved.</li>
</ul>
<h3>Options</h3>
<ul>
<li><code>--threshold</code>: Probability threshold for identifying ditch pixels. Default is <code>0.5</code>.</li>
<li><code>--tolerance</code>: Pixel dilation tolerance for identifying changes. Default is <code>2</code>.</li>
<li><code>--buffer</code>: Buffer distance around old ditches to filter overlaps. Default is <code>3</code>.</li>
</ul>
<h3>Example</h3>
<div class="code-block-parent">
<div class="code-block-container">
<button aria-label="Copy code" class="copy-code-button"><i aria-hidden="true" class="aalto-icon aalto-icon--copy"></i></button>
<pre style="overflow-x: auto;"><code class="language-bash">python find_new_ditches.py new_rasters\ old_rasters\ output --threshold 0.55 --tolerance 2 --buffer 3
</code></pre>
</div>
</div>
<h2>Outputs</h2>
<p>The script generates the following outputs inside the specified output directory:</p>
<ul>
<li>Merged raster files for new and old layers (<code>merged_new.tif</code>, <code>merged_old.tif</code>).</li>
<li>Difference raster identifying new ditches (<code>new_only_raster.tif</code>).</li>
<li>Vector layer of new ditch segments (<code>new_ditches_vectorized.gpkg</code>).</li>
<li>Filtered vector layer with overlaps removed (<code>new_ditches_vectorized_filtered.gpkg</code>).</li>
</ul>
<h2>Notes</h2>
<ul>
<li>Ensure that the directories specified for new and old layers contain <code>.tif</code> files.</li>
<li>Output vector and raster files will be saved in the specified output directory.</li>
<li>Open "new_ditches_vectorized.gpkg" for example in QGIS for further analysis</li>
</ul>
