"""
Demonstration code illustrating the principles of a neural network.
It does not use any ready-made computational modules, creating the
neural network "from scratch" using only Python's built-in functions.

The only external library used in this example is matplotlib
(run `pip install matplotlib` to install it).

This neural network attempts to learn a hidden function `hidden_function`
from a set of individual points randomly scattered around the graph of this
function.

To see the model in action, you can define your own function and also
"play around" with the model's global variables:

1) BATCH_SIZE - the size of the subset (a subset of points from all points
   around the graph that the model learns from).
2) EPOCHS - the number of training cycles
3) LEARNING_RATE - the "step size" in training. Affects the balance between
   speed and accuracy.
4) LAYERS_CONFIG - the neural network configuration. Each tuple in the array
   describes a separate layer: the number of neurons in the previous layer,
   the number of neurons in the next layer, and the activation function.
   Important: Since this example solves a scalar problem — finding the
   value of the theoretically ideal function y(x) for a given scalar x —
   the first and last layers of the network should contain 1 neuron each.
   The last layer must always have a linear activation function.

Example neural network configuration:
[
    (1, 5, 'tanh'),   # Hidden layer
    (5, 3, 'tanh'),   # Hidden layer
    (3, 1, 'linear')  # Output layer
]

This corresponds to the following neuron distribution:

      ┌ X ┐
      │ X ├ X ┐ 
─> X ─┤ X │ X ├ X ─>
      │ X ├ X ┘
      └ X ┘
"""

from typing import cast
import math
import random
import copy
import matplotlib.pyplot as plt


def hidden_function(x: float):
    """
    The hidden function describing the real process
    that the model is trying to predict based on
    individual observed data points.
    """
    return 3 * x ** 2 + 5


BATCH_SIZE = 20
EPOCHS = 300
LEARNING_RATE = 5e-2

# Network creation
LAYERS_CONFIG = [
    (1, 8, 'tanh'),   # Hidden layer
    (8, 1, 'linear')  # Output layer
]


###############################################
# Main code. Do not modify below this comment #
###############################################

XRANGE = [x / 100 for x in range(-100, 100)]

# Type annotation
Point = tuple[float, float]
Points = list[Point]


def create_dataset() -> "Points":
    """
    Simulates a simple scatter of observed data
    around the theoretical function y(x). The model
    will use this data to predict the theoretical function.
    """
    return [
        (x, hidden_function(x) + random.gauss(0, sigma=0.4))
        for x in XRANGE
    ]


class Layer:
    """
    Class representing the behavior of neurons in a
    single layer of a neural network.
    """

    def __init__(self, input_dim: int,
                 output_dim: int,
                 activation: str = "linear"):

        # Dimensions of the current and next layer,
        # as well as the type of activation function for neurons in the layer
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.activation_name = activation

        # To store weights and biases
        self.W = [[random.uniform(-1, 1) for _ in range(input_dim)]
                  for _ in range(output_dim)]
        self.b = [random.uniform(-1, 1) for _ in range(output_dim)]

        # To store gradients
        self.grad_W = [[0.0 for _ in range(input_dim)]
                       for _ in range(output_dim)]
        self.grad_b = [0.0 for _ in range(output_dim)]

        # Accumulators (for accumulating gradients) for the batch
        self.accum_grad_W = [
            [0.0 for _ in range(input_dim)] for _ in range(output_dim)]
        self.accum_grad_b = [0.0 for _ in range(output_dim)]

        # Selection of the activation function
        if activation == "tanh":
            self.activation = math.tanh
            self.d_activation = lambda z: 1 - math.tanh(z) ** 2
        elif activation == "linear":
            self.activation = lambda z: float(z)
            self.d_activation = lambda z: 1.0
        else:
            raise ValueError(f"Unknown activation: {activation}")

    def forward(self, inputs: list[float]):
        """
        Forward pass through the layer. For each neuron,
        computes the activation function A(z[i]), where
        z[i] = Σ x[j]·W[i][j] + b[i]. The array of activations
        is stored in the `.outputs` attribute of the layer instance.

        :param inputs: This is x[j] in the formula — an array of
            activations from the previous layer.
        """
        self.inputs = inputs  # store for backward propagation
        self.z = []

        # Linear combination z[i]
        for i in range(self.output_dim):
            zi = sum(self.W[i][j] * inputs[j] for j in range(self.input_dim))
            zi += self.b[i]
            self.z.append(zi)

        # Apply activation A(z[i])
        self.outputs = [self.activation(zi) for zi in self.z]
        return self.outputs

    def backward(self, grad_outputs: list[float]):
        """
        Returns the gradient of the loss function L with respect to the output y_predict[j]
        for each j-th neuron of the previous layer. Since the output of the previous layer's
        neuron is the input x[j] of the current layer, the gradient ∇L[y_predict] = ∇L[x] = dL/dx[j].
        This is known as backpropagation for the mean squared error.

        Intermediate gradients for the current layer are computed and stored for the loss function L(W, b):

        - Weight gradient ∇L[W] 
        - Bias gradient ∇L[b] 

        :param grad_outputs: derivatives of the activation function dL/dA(z[i])
        :returns: ∇L[x]
        """
        # Gradients with respect to z (including the derivative
        # of the activation function)
        # ∇L[z] = dL/dz[i] = dL/dA·dA/dz[i]
        grad_z = []
        for i in range(self.output_dim):
            d_act = self.d_activation(self.z[i])
            grad_z.append(grad_outputs[i] * d_act)

        # Gradients of weights abd biases
        # ∇L[W] = dL/dW[i][j] = dL/dz[i]·dz[i]/dW[i][j]
        # ∇L[b] = dL/db[i]    = dL/dz[i]·dz[i]/db[i]
        # Since z[i] = Σ x[j]·W[i][j] + b[i], hence
        # ∇L[W] = dL/dW[i][j] = dL/dz[i]·x[i]
        # ∇L[b] = dL/db[i]    = dL/dz[i]
        self.grad_W = [[0.0] * self.input_dim for _ in range(self.output_dim)]
        self.grad_b = [0.0] * self.output_dim

        for i in range(self.output_dim):
            for j in range(self.input_dim):
                self.grad_W[i][j] = grad_z[i] * self.inputs[j]
            self.grad_b[i] = grad_z[i]

        # Gradients for preceding layer
        # ∇L[x] = dL/dx[j] = Σ dL/dz[i]·dz[i]/dx[j]
        # Since z[i] = Σ x[j]·W[i][j] + b[i]
        # then ∇L[x] = Σ dL/dz[i]·W[i][j]
        grad_inputs = [0.0] * self.input_dim
        for j in range(self.input_dim):
            grad_inputs[j] = sum(
                grad_z[i] * self.W[i][j] for i in range(self.output_dim)
            )

        return grad_inputs

    def update(self, learning_rate: float):
        """
        Updates the current weights and biases of the layer's neurons
        by a fraction λ of the weight gradients ∇L[W] and bias gradients ∇L[b]
        in the current step of gradient descent.

        :param learning_rate: Fraction λ of the gradients
        """
        for i in range(self.output_dim):
            for j in range(self.input_dim):
                self.W[i][j] -= learning_rate * self.grad_W[i][j]
            self.b[i] -= learning_rate * self.grad_b[i]


class NeuralNetwork:
    """
    Wrapper class that combines multiple individual layers
    into a single larger neural network.
    """

    def __init__(self,
                 layers_config: list[tuple],
                 learning_rate: float = 1e-2):
        """
        Neural network initializer from multiple layers.

        :param layers_config: list of tuples defining each layer of the network
            as (input_dim, output_dim, activation).
            Example: [(1, 8, 'tanh'), (8, 1, 'linear')].
        :param learning_rate: global model parameter affecting the balance
            between training speed and accuracy.
        """
        self.layers = cast(list[Layer], [])
        for config in layers_config:
            layer = Layer(*config)
            self.layers.append(layer)

        self.learning_rate = learning_rate

    def forward(self, x: float) -> tuple[float, dict]:
        """
        Forward pass through the entire neural network.

        Sequentially passes the input through all layers of the network,
        computing the output of each layer and the final prediction of the model.

        Algorithm:
        1. The input value x is interpreted as a feature vector
        (in this case one-dimensional — the coordinate of an observed point from
        the dataset).
        2. For the current layer, the forward transformation is computed:
        layer input (vector) = y_pred from the previous layer, and for each
        i-th neuron in the current layer:
            z[i] = Σ_j W[i][j] * y_pred_prev[j] + b[i]
            y_pred[i] = A(z[i])
        where 
        - the summation is over all neurons j in the previous layer,
        - W[i][j] is the weight between the j-th neuron of the previous layer
            and the i-th neuron of the current layer,
        - b[i] is the bias of the i-th neuron of the current layer,
        - A is the activation function of the current layer.
        3. Intermediate inputs and outputs of layers are stored for
        later use in backpropagation.

        :param x: input value (feature). In this task — the x-coordinate
            of an observed point located near the true function graph.
        :return: tuple (y_pred, cache), where:
            - y_pred: scalar network output (prediction)
            - cache: stored intermediate values from the forward pass
            (layer inputs and outputs) needed for backpropagation.
        """
        inputs = [x]
        cache: dict[str, list[list[float]]] = {"inputs": [], "outputs": []}

        for layer in self.layers:
            cache["inputs"].append(inputs)
            inputs = layer.forward(inputs)
            cache["outputs"].append(inputs)

        return inputs[0], cache

    def backward(self, y_true: float, y_pred: float, cache: dict):
        """
        Backpropagation through the entire neural network.

        Performs backpropagation starting from the output layer and moving
        towards the input, sequentially computing the gradients of the loss
        function with respect to the parameters of each layer and the outputs
        of previous layers.

        Algorithm:
        1. Compute the gradient of the loss function with respect to the network output:
        dL/dy_pred for the mean squared error (loss function L).
        2. Pass the resulting gradient to the last (final) layer.
        3. Each layer receives the gradient with respect to its output and returns
        the gradient with respect to its input, which is used by the next
        (previous in order) layer.

        During this process, each layer:
        - computes and stores gradients ∇L[W] and ∇L[b]
        - returns ∇L[x], where x is the input to that layer
        (the output of the previous layer)

        :param y_true: true value of the target variable from the dataset
        :param y_pred: value predicted by the network
        :param cache: stored intermediate values from the forward pass
                    (used by layers to compute gradients)
        """
        # Gradiend of loss function L
        grad = [2 * (y_pred - y_true)]

        # Iterate from the last layer to the first layer
        for layer in reversed(self.layers):
            grad = layer.backward(grad)

    def train_batch(self, batch: Points):
        """
        Training on a batch.

        :param batch: subset of observed data from the dataset
        """
        total_loss = 0.0

        # Accumulating gradients
        for layer in self.layers:
            # Create temporary accumulators
            layer.accum_grad_W = [[0.0] * layer.input_dim
                                  for _ in range(layer.output_dim)]
            layer.accum_grad_b = [0.0] * layer.output_dim

        for x, y_true in batch:
            y_pred, cache = self.forward(x)
            total_loss += (y_pred - y_true) ** 2

            self.backward(y_true, y_pred, cache)

            # Accumulate gradients
            for layer in self.layers:
                for i in range(layer.output_dim):
                    for j in range(layer.input_dim):
                        layer.accum_grad_W[i][j] += layer.grad_W[i][j]
                    layer.accum_grad_b[i] += layer.grad_b[i]

        # Averaging and updating
        batch_size = len(batch)
        for layer in self.layers:
            layer.grad_W = layer.accum_grad_W
            layer.grad_b = layer.accum_grad_b
            # Mean value of the gradients
            for i in range(layer.output_dim):
                for j in range(layer.input_dim):
                    layer.grad_W[i][j] /= batch_size
                layer.grad_b[i] /= batch_size
            layer.update(self.learning_rate)

        return total_loss / batch_size

    def train_epoch(self, dataset: Points, batch_size: int):
        """
        Training for one epoch

        :param dataset: a sample of actually observed data — feature-value pairs.
            In our case, these are coordinates of points scattered around the graph
            of the theoretical function that the model is trying to predict.
        :param batch_size: size of the subset used for training in the current epoch
        """
        dataset_copy = copy.deepcopy(dataset)
        random.shuffle(dataset_copy)

        total_loss = 0.0
        num_batches = 0

        for i in range(0, len(dataset_copy), batch_size):
            batch = dataset_copy[i:i + batch_size]
            batch_loss = self.train_batch(batch)
            total_loss += batch_loss
            num_batches += 1

        return total_loss / num_batches if num_batches > 0 else 0.0


def plot_data(net: NeuralNetwork,
              losses: list[float],
              dataset: Points):
    """
    Displays a plot on the left showing the decrease of the loss
    (mean squared error) over epochs, illustrating the convergence dynamics.
    On the right, it shows the theoretical function, the points scattered
    around it (actual observed data from the dataset), and the model's prediction.
    """
    # real data
    x_real = [p[0] for p in dataset]
    y_real = [p[1] for p in dataset]

    # theoretical function to predict
    y_nature = [hidden_function(xi) for xi in x_real]

    # predicted function
    y_pred = [net.forward(xi)[0] for xi in x_real]

    # Create figure with two subplots
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Loss per epoch chart
    ax1.plot(range(len(losses)), losses, label="Losses Per Epoch")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("MSE")
    ax1.set_title("Losses Per Epoch")
    ax1.legend()

    # Real vs predicted function
    ax2.scatter(x_real, y_real,
                s=10,
                alpha=0.3,
                color='green',
                label='Data')
    ax2.plot(x_real, y_pred, label="Predicted function", linestyle='--')  # line
    ax2.plot(x_real, y_nature, label="Real function")  # libe
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_title("Data Scatter and Approximation")
    ax2.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    dataset = create_dataset()
    net = NeuralNetwork(LAYERS_CONFIG, learning_rate=LEARNING_RATE)

    # Learning
    losses = []
    for epoch in range(EPOCHS):
        loss = net.train_epoch(dataset, BATCH_SIZE)
        losses.append(loss)

    plot_data(net, losses, dataset)
