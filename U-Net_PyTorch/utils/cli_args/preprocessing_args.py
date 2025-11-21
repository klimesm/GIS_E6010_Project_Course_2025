def add_preprocessing_args(parser):
    parser.add_argument("input_dem_dir", help="Generate training or testing chips from DEM and vector data.")
    parser.add_argument("label_vector_data",
                        help="Vector dataset containing labeled ditch features (e.g., .shp, .gpkg).")

    parser.add_argument("output_dir", help='Directory where output "training_data" directory including'
                                           'feature and label chips will be written.')

    parser.add_argument("--mode", choices=["train", "test"], default="train",
                        help='Dataset generation mode: "train" for training data, "test" for test data.')

    parser.add_argument("--label_hpmf_threshold",
                        type=float,
                        default=-0.075,
                        help="Keep pixels with HPMF ≤ threshold as label; higher values are ignored.")