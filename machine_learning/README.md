# Neural Network Demonstration

Demonstration code illustrating the principles of a neural network. It does not use any ready-made computational modules, creating the neural network "from scratch" using only Python's built-in functions.

The only external library used in this example is **matplotlib** (run `pip install matplotlib` to install it).

This neural network attempts to learn a hidden function `hidden_function` from a set of individual points randomly scattered around the graph of this function.

## How to Use

To see the model in action, you can define your own function and also "play around" with the model's global variables:

1. **BATCH_SIZE** – the size of the subset (a subset of points from all points around the graph that the model learns from).
2. **EPOCHS** – the number of training cycles.
3. **LEARNING_RATE** – the "step size" in training. Affects the balance between speed and accuracy.
4. **LAYERS_CONFIG** – the neural network configuration. Each tuple in the array describes a separate layer:
   - Number of neurons in the previous layer
   - Number of neurons in the next layer
   - Activation function

   > **Note:** Since this example solves a scalar problem — finding the value of the theoretically ideal function `y(x)` for a given scalar `x` — the first and last layers of the network should contain 1 neuron each. The last layer must always have a linear activation function.

## Example Neural Network Configuration

```python
LAYERS_CONFIG = [
    (1, 5, 'tanh'),   # Hidden layer
    (5, 3, 'tanh'),   # Hidden layer
    (3, 1, 'linear')  # Output layer
]
```

This corresponds to the following neuron distribution:

```
      ┌ X ┐
      │ X ├ X ┐
─> X ─┤ X │ X ├ X ─>
      │ X ├ X ┘
      └ X ┘
```
