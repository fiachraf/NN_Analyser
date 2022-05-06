import os
import csv
import numpy as np
from matplotlib import pyplot as plt
import time
from os.path import dirname
#ensures that tensorflow is used as the backend
import tensorflow as tf
#tf.compact.v1.keras.backend.set_session()
tf.config.threading.set_intra_op_parallelism_threads(16)
tf.config.threading.set_inter_op_parallelism_threads(16)

#from keras.backend.tensorflow_backend import set_session
#import  tf.keras.backend.tensorflow_backend as K
#taken from Francis Chollet - Deep Learning with Python, starting page 147
#import keras
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import models

from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing import image_dataset_from_directory
model_name = input("enter the full path of model: ") or "/home/fiachra/atom_projects/meteorml/keras/meteorml_20220220_4.h5"
CNN_model = models.load_model(model_name)

initial_dir = os.getcwd()

folder_input = input("folder containing folders labelled 0 and 1 respectively that contain images that you want to test false identification: ") or "/home/fiachra/Downloads/Meteor_Files/20210131_pngs"
# start_time = time.perf_counter()
#need to check which is confirmed and which is negative 0 or 1
#initialise list of predictions, elements are tuples (Label, prediction, false_pred, file_name)
#Label = 1 for Confirmed files, 0 for Rejected files, prediction = prediction value from neural network has value between 0 and 1, false_pred = Boolean true or false if the prediction is < 55% for Confirmed images or >45% for Rejected images it is considered false, file_name is the name of the .png file
# Confidence of less than 55% from prediction is considered false as it may be interesting to see which predictions the network is very unsure about
pred_list = []

def false_pred(actual_label, predicted_label):
    if abs(actual_label - predicted_label) < 0.45:
        return True
    else:
        return False
def get_label(file_name):
    label_1_or_0 = int(dirname(file_name)[-1])
    return label_1_or_0



#noramlisaton functions, can be done using keras preprocessinglayers which are present in newer versions of tensorflow, I am using tensorflow 2.4.1 I had a reson for this specific verions but I just can't remember
def normalise_me(image, label):
    image = tf.cast(image/255., tf.float32)
    return image, label

def center_me(image, label):
#image is really a batch of images and so axis=[1,2,3] and keepdims=True is needed so that it gets the mean and standard deviation for each individula image rather than across the batch
    mean_1 = tf.math.reduce_mean(image, axis=[1,2,3], keepdims=True)
    image = image - mean_1
    return image, label

def standardise_me(image, label):
    std_val = tf.math.reduce_std(image, axis=[1,2,3], keepdims=True)
    image = image / std_val
    return image, label

#I only used this function for some of my later machine learning algorithms
#If accuracy from this script doesn't mathc self reported accuracy from keras then this migh need to be utilised/not utilised, would need to change line 96 ish
def rescale_2(image, label):
    max_val =tf.math.reduce_max(tf.math.abs(image), axis=[1,2,3], keepdims=True)
    image = image / max_val
    return image, label


# make a tf.dataset generator list
data_dir = folder_input
file_dataset = image_dataset_from_directory(
   data_dir,
   labels="inferred",
   color_mode = "grayscale",
   batch_size=32,
   #don't forget to change image size depending on network
   image_size = (32,32),
   shuffle=False,
   interpolation = "bilinear")
labels_list = []
#for x, y in file_dataset:
#   labels_list.append(y)

#have to apply the transofrmations like this, doesn't seem to work to modify the dataset in place
file_dataset_norm = file_dataset.map(normalise_me)
file_dataset_cent = file_dataset_norm.map(center_me)
file_dataset_stan = file_dataset_cent.map(standardise_me)
file_dataset_resc2 = file_dataset_stan.map(rescale_2)


#getting the weights and biases of each layer
# weights_0, biases_0 = CNN_model.layers[0].get_weights()   # using CNN_script_20220220_4.py model layer 0 is a convolution layer
# weights_1, biases_1 = CNN_model.layers[1].get_weights()   # layer 1 is a max pool layer so it has no weights or biases
# weights_2, biases_2 = CNN_model.layers[2].get_weights()   # layer 2 is a Flatten layer so it has no weights or biases
# weights_3, biases_3 = CNN_model.layers[3].get_weights()     # layer 3 is a dense layer
# weights_4, biases_4 = CNN_model.layers[4].get_weights()     # layer 4 is the dense final layer

# print(f"weights_3: {weights_3}\nbiases_3: {biases_3}")

CNN_model.summary()


#defining my classes
# for layer in CNN_model.layers:
    # print(layer.output_shape)


class NN_neuron:
    def __init__(neuself, neuron_index, parent_layer):
        neuself.neuron_index = neuron_index
        neuself.parent_layer = parent_layer
        neuself.type = parent_layer.layer_type
        neuself.weights = None
        neuself.bias = None
        neuself.act_val = None
        neuself.labels = None
        neuself.mean = 0
        neuself.max = None
        neuself.min = None
        neuself.num_inputs = 0

    def neuron_weighting(neuself, weighting, biasing):
        neuself.weights = weighting
        neuself.bias = biasing
    #leaving this one here so you can get the activation for a single image input
    def neuron_activation(neuself, act):
        # print(f"type(act): {type(act)}")
        if act.all() == None:
            act = np.zeros(act.shape)
        neuself.act_val = act
        neuself.update_vals(act)

    def update_vals(neuself, new_act):
        if neuself.num_inputs == 0:
            neuself.max = new_act
            neuself.min = new_act

        elif np.mean(new_act) > np.mean(neuself.max):
            neuself.max = new_act
        elif np.mean(new_act) < np.mean(neuself.min):
            neuself.min = new_act
        neuself.running_average(new_act)
        neuself.num_inputs += 1

    def running_average(neuself, new_act_1):
        # print("test1")
        # print(neuself.mean)
        # if neuself.mean == None:
        #     neuself.mean = new_act_1
        # else:
        neuself.mean = ((neuself.mean * neuself.num_inputs) + new_act_1) / (neuself.num_inputs + 1)

class NN_layer:
    def __init__(layself, layer_index, parent_net):
        layself.layer_index = layer_index
        layself.parent_net = parent_net
        layself.layer_type = parent_net.NN_model.layers[layer_index].__class__.__name__
        layself.layer_shape = parent_net.NN_model.layers[layer_index].output_shape
        layself.neuron_list = []
        """
        #layer_shape should be tensor.
        #1st axis is None as it can be a tensor that consists of many instances of the tensor to be fed into the neural network
        #details of other axes will depend on layer type, e.g. for a Conv2D layer, 2nd & 3rd axis for grayscale images will be the output image size
        #I think it should be the last axis that will be the number of outputs of a layer
        """

        layself.num_neurons = layself.layer_shape[-1]
        #create instances of all the neurons in the layer
        for neuron_index in range(layself.num_neurons):
            layself.neuron_list.append(NN_neuron(neuron_index, layself))
            #distribut weights and biases after everything has been initialised

        #len of layer_list is 0 as the NN_layer object hasn't finished being created and so hasn't been added to the list yet

    def layer_weighting(layself):
        #need self argument as methods in classes are designed to have themselves as an argument
        try:
            layer_weights, layer_biases = layself.parent_net.NN_model.layers[layself.layer_index].get_weights()
        except ValueError:
            layer_weights, layer_biases = None, None
            #any layers that don't have weights or biases like MaxPooling2D or Flatten will cause the try statement to give an error
        #adding weights to the neurons in the layer
        # TODO:  replace layer specific indexing with array[..., :] for indexing. Indexes/slices in the last dimension regardless of number of axes
        for index_1, neuron_object in enumerate(layself.neuron_list):
            if layself.layer_type == "Conv2D":  #Conv2D layer has shape (mask_dim1, mask_dim2, mask_dim3, number of neurons), so need to slice in the last axis
                neuron_object.neuron_weighting(layer_weights[:,:,:,index_1], layer_biases[index_1])
            elif layself.layer_type == "Dense": #Dense layer has shape (weight, number of neurons) so again slice in the last axis
                neuron_object.neuron_weighting(layer_weights[:,index_1], layer_biases[index_1])
            else:
                #should be the case for MaxPooling2D and Flatten layers
                neuron_object.neuron_weighting(layer_weights, layer_biases)

    def dist_layer_activations(layself, act_array):
        #act array is a numpy array that has shape (len(input_list), (shape for n Dimensional layer like Conv2D), number of neurons)
        #for each input/image
        for index_2, input_n_activation in enumerate(act_array):
            #for each neuron in layer
            for neuron_object_1 in layself.neuron_list:
                neuron_object_1.neuron_activation(input_n_activation)
            # layself.neuron_list[index_2].neuron_activation(input_n_activation[..., index_2])

        # for neuron_index_1, neuron_object_1 in enumerate(layself.neuron_list):
        #     neuron_object_1.neuron_activation(act_array[..., neuron_index_1])
        #act_array is the array of activation values for this layer for the input given to the Neural_Net




class Neural_Net:
    def __init__(Netself, NN_model):
        Netself.NN_model = NN_model
        Netself.num_layers = len(NN_model.layers)
        Netself.layer_list = []

        for layer_index in range(len(Netself.NN_model.layers)):
            Netself.layer_list.append(NN_layer(layer_index, Netself))
            #generates instance of NN_layer class and adds to list, then get the weights for the just added layer.
            #Done this way as NN_layer class refers to items in this list when adding weights
            Netself.layer_list[-1].layer_weighting()


            #create custom layer class instance for each layer in neural network
            # setattr(self, f"layer_{layer_index}", NN_layer(self.NN_model.layers[layer_index].output_shape, f"layer_{layer_index}", self.NN_model.layers[layer_index].__class__.__name__))

    def get_layer_activations(self):
        pass
    def get_all_layers_activations(Netself):
        layers_outputs = [layer.output for layer in Netself.NN_model.layers]
        activation_model = models.Model(inputs=Netself.NN_model.input, outputs = layers_outputs)
        activations = activation_model.predict(file_dataset_resc2)
        #distribute the activations layer by layer
        for layer_index_1, layer_activations in enumerate(activations):
            Netself.layer_list[layer_index_1].dist_layer_activations(layer_activations)

        #activations is a list of length = number of layers
        #each element of the list is a numpy array
        #each numpy array has shape (len(input list), ... , number of neurons in layer), layers that have an image output like (len(input list), x_image_size, y_image_size, channels(if colour image), number of neurons in layer)
        return activations

Chosen_Neural_Network = Neural_Net(CNN_model)

layer_activations = Chosen_Neural_Network.get_all_layers_activations()
# for layer in layer_activations:
    # print(f"type(layer): {type(layer)}")
    # print(f"layer.shape: {layer.shape}")
# print(f"len(activations): {len(Chosen_Neural_Network.get_all_layers_activations())}")




# for object in Chosen_Neural_Network.layer_list:
#     print(f"num_neurons: {object.num_neurons}")
#     print(f"len(object.neuron_list): {len(object.neuron_list)}")
#     print(f"object.neuron_list[0].weights: {object.neuron_list[0].weights}")
# print()

print(Chosen_Neural_Network.layer_list[0].neuron_list[0])
print(f"neuron index: {Chosen_Neural_Network.layer_list[0].neuron_list[0].neuron_index}")
print(f"parent layer: {Chosen_Neural_Network.layer_list[0].neuron_list[0].parent_layer}")
print(f"weights : {Chosen_Neural_Network.layer_list[0].neuron_list[0].weights}")
print(f"bias: {Chosen_Neural_Network.layer_list[0].neuron_list[0].bias}")
print(f"act_val: {Chosen_Neural_Network.layer_list[0].neuron_list[0].act_val}")
print(f"mean: {Chosen_Neural_Network.layer_list[0].neuron_list[0].mean}")
print(f"max: {Chosen_Neural_Network.layer_list[0].neuron_list[0].max}")
print(f"min: {Chosen_Neural_Network.layer_list[0].neuron_list[0].min}")


# test = CNN_model.input
# print(test)

# layer_outputs = [layer.output for layer in CNN_model.layers[:]]
# layer_output = CNN_model.layers[-2].output
# activation_model = models.Model(inputs=CNN_model.input, outputs=layer_output)
# activations = activation_model.predict(file_dataset_resc2)
# print(activations)
# print(f"type(activations): {type(activations)}")
# print(f"activations.shape {activations.shape}")



"""
#predictions section:

image_paths = file_dataset.file_paths
pred_distribution_list = []
prediction_list = []
#index varaible used to keep track of file names as images are loaded in batches while the filenames is just one long list
index = 0
for images_batch, labels_batch in file_dataset_resc2:
    #does the prediction for a batch of images
    prediction = CNN_model.predict(images_batch)

    print(f"batch {(index + 1)/ 32} of {len(image_paths) / 32}")
    activations = activation_model.predict(images_batch)
    print(f"batch activations: {activations.shape}")

    #for each image in the batch
    for index_2, image in enumerate(images_batch):
        #get the image label
        label_numpy = labels_batch[index_2].numpy()
        #get the prediction for the image from the prediction tensor returned from the prediction on the batch of images
        #need the [index_2][0] slice as the [index_2] slice is an EagerTensor and the [0] slice then gets the actual value out of the EagerTensor
        pred = round(prediction[index_2][0], 2)
        pred_distribution_list.append(pred)
        #add details of each images prediction to the list to be written out later
        prediction_list.append((label_numpy, pred, false_pred(label_numpy, pred), image_paths[index]))



        index += 1




os.chdir(initial_dir)

print(f"len(prediction_list): {len(prediction_list)}")


log_file_name = f"{model_name[:-3]}_false_iden_log_singly_tf.csv"
with open(log_file_name, "w") as csv_logfile:
    csv_logfile_writer = csv.writer(csv_logfile, delimiter=",")
    csv_logfile_writer.writerow(["Label", "Prediction", "True Prediction", "File Name"])
    for label_1, pred_1, false_pred_1, file_name_1 in prediction_list:
        csv_logfile_writer.writerow([label_1, pred_1, false_pred_1, file_name_1])



#need as input for hist function to be list of all pred values in pred_list
fig = plt.hist(pred_distribution_list, bins=100)
plt.title("Prediction_distribution")
plt.xlabel("Prediction")
plt.ylabel("No. of predictions")
plt.savefig(f"{model_name[:-3]}_pred_dist_singly_tf.png")

# end_time = time.perf_counter()
# print(f"time elapsed: {end_time - start_time}")

"""
