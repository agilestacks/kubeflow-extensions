import tensorflow as tf

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# Parsing flags.
parser = argparse.ArgumentParser()
parser.add_argument("--input_hdf5_model")
parser.add_argument("--output_model_path")
parser.add_argument("--mkdirs", type=bool, default=False)
parser.add_argument("--tempfile", default=True)

args = parser.parse_args()
hdf5_model = args.input_hdf5_model

if tf.tempfile:
    # Workaround because of: at present goofys support only parallel write
    # see: https://github.com/kahing/goofys/issues/298
    # TODO configure h5py to write sequentially
    # TODO consider other flex driver
    _, export_path = tempfile.mkdtemp()
else:
    export_path = args.output_tf_model_path

print(f"Loading hdf5 model from: {hdf5_model}")

# The export path contains the name and the version of the model
tf.keras.backend.set_learning_phase(0)  # Ignore dropout at inference
model = tf.keras.models.load_model(hdf5_model)

if args.mkdirs:
    os.makedirs(export_path)

# Fetch the Keras session and save the model
# The signature definition is defined by the input and output tensors
# And stored with the default serving key
print(f"Saving to {export_path}")
with tf.keras.backend.get_session() as sess:
    tf.saved_model.simple_save(
        sess,
        export_path,
        inputs={'input_image': model.input},
        outputs={t.name: t for t in model.outputs})

if args.tempfile:
    print(f"Exporting to {args.output_model_path}")
    os.makedirs(args.output_model_path)
    shutil.copytree(export_path, args.output_model_path)

print("Done!")
