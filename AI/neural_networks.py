from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print(gpus)
if gpus:
	# Restrict TensorFlow to only allocate 1GB of memory on the first GPU
	try:
		tf.config.set_logical_device_configuration(
        gpus[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=15000)])
		logical_gpus = tf.config.list_logical_devices('GPU')
		print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
	except RuntimeError as e:
		# Virtual devices must be set before GPUs have been initialized
		print(e)

def policy_NN():
	tf.config.list_physical_devices('GPU')
	# inits the policy Neural Network
	policy = keras.models.Sequential(name="policy")
	policy.add(layers.Conv2D(18, (2, 2), padding='valid', activation='relu', input_shape=(18, 8, 8)))
	policy.add(layers.MaxPool2D((2, 2)))
	policy.add(layers.Conv2D(28, (2, 2), activation='relu'))
	policy.add(layers.MaxPool2D((2, 2)))
	policy.add(layers.Flatten())
	policy.add(layers.Dense(536, activation='relu'))
	policy.add(layers.Dense(218, activation='softmax'))
	loss = keras.losses.CategoricalCrossentropy()
	optim = keras.optimizers.Adam(learning_rate=0.2)
	metrics = ["accuracy"]
	policy.compile(optimizer=optim, loss=loss, metrics=metrics)
	policy.summary()
	return policy


def value_NN():
	# inits the value Neural Network
	value = keras.models.Sequential(name="value")
	value.add(layers.Conv2D(18, (2, 2), padding='valid', activation='relu', input_shape=(18, 8, 8)))
	value.add(layers.MaxPool2D((2, 2)))
	value.add(layers.Conv2D(32, (2, 2), activation='relu'))
	value.add(layers.MaxPool2D((2, 2)))
	value.add(layers.Flatten())
	value.add(layers.Dense(56, activation='relu'))
	value.add(layers.Dense(1, activation='relu'))
	loss = keras.losses.MeanSquaredError()
	optim = keras.optimizers.Adam(learning_rate=0.2)
	metrics = ["accuracy"]
	value.compile(optimizer=optim, loss=loss, metrics=metrics)
	value.summary()
	return value


def load_model(new_model: bool, policy_save_path: str, value_save_path: str):
	if new_model:
		policy_network = policy_NN()
		value_network = value_NN()
	else:
		policy_network = keras.models.load_model(policy_save_path)
		value_network = keras.models.load_model(value_save_path)
	return policy_network, value_network

def init_network_paths() -> tuple:
	new_policy_save_path = "AI/neural_networks/policy_new.keras"
	new_value_save_path = "AI/neural_networks/value_new.keras"
	value_save_path = "AI/neural_networks/value.keras"
	policy_save_path = "AI/neural_networks/policy.keras"
	return new_policy_save_path, new_value_save_path, value_save_path, policy_save_path


def save_model(new_value_network: tf.keras.models, new_policy_network: tf, old_value_network: tf, old_policy_network: tf, paths: tuple):
	new_policy_save_path, new_value_save_path, value_save_path, policy_save_path = paths
	# save the networks
	new_policy_network.save(new_policy_save_path)
	new_value_network.save(new_value_save_path)
	old_policy_network.save(policy_save_path)
	old_value_network.save(value_save_path)

def init_single_network_paths():
	return "AI/neural_networks/value.keras", "AI/neural_networks/policy.keras"


value_path, policy_path = init_single_network_paths()
POLICY_NETWORK, VALUE_NETWORK = load_model(new_model=False, policy_save_path=policy_path, value_save_path=value_path)
print("model loaded")