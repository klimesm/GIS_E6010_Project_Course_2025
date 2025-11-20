def add_training_args(parser):
    group = parser.add_argument_group("Training options")

    group.add_argument("feature_dir", help="Path to directory containing input feature images.")
    group.add_argument("label_dir", help="Path to directory containing label (mask) images.")
    group.add_argument("max_epochs", type=int, help="Maximum number of training epochs to run.")

    group.add_argument("--batch_size",
                       type=int,
                       default=4,
                       help="Batch size for training.")

    group.add_argument("--num_workers",
                       type=int,
                       default=0,
                       help="Number of parallel CPU workers used for loading batches from disk.")

    group.add_argument("--compute_precision",
                       choices=["16-true", "16-mixed",
                                "bf16-true", "bf16-mixed",
                                "32-true", "64-true",
                                "64", "32", "16", "bf16"],

                       default="32-true",
                       help="Computation precision for training. More info: "
                            "https://lightning.ai/docs/pytorch/stable/common/precision_basic.html")
