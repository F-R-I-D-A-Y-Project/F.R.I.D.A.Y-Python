import torch.nn as nn
import torch
import torch.nn.functional as F
import torchtext
import math
import tiktoken
import warnings
import csv, pickle
import pathlib
import subprocess
import sys
import pathlib
from typing import Self

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

from model.dbreader import DBReader

warnings.simplefilter("ignore")

class UntrainedModelError(Exception):
    pass


class Transformer(nn.Module):
    def __init__(self: Self,
                 device: torch.device) -> None:
        super().__init__()


class Model:
    '''
        This class is responsible for the NLP model of the chatbot.
    '''
    def __init__(self: Self, path_to_dataset: str,
                 batch_size: int=32,
                 block_size: int=8,
                 max_iters: int=3000,
                 eval_interval: int=300,
                 learning_rate: float=1e-2,
                 eval_iters: int=200,
                 encoding: str='gpt2') -> None:
        '''
            Constructor of the class. It receives the path to the dataset, but does not train the model.
            
            Args:
                path_to_dataset (str): path to dataset used for training
        '''
        self.__dataset = path_to_dataset
        self.__device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.__batch_size = batch_size
        self.__block_size = block_size
        self.__max_iters = max_iters
        self.__eval_interval = eval_interval
        self.__learning_rate = learning_rate
        self.__eval_iters = eval_iters
        self.__enc = None
        try:
            self.__enc = tiktoken.get_encoding(encoding)
        except ValueError:
            self.__enc = tiktoken.encoding_for_model(encoding)            

    @property
    def dataset(self: Self) -> str:
        '''
            This property returns the path to the dataset.
        '''
        return self.__dataset
    
    @property
    def device(self: Self) -> torch.device:
        '''
            This property returns the device used for the model.
        '''
        return self.__device
    
    @property
    def batch_size(self: Self) -> int:
        '''
            This property returns the batch size used for training the model.
        '''
        return self.__batch_size
    
    @property
    def block_size(self: Self) -> int:
        '''
            This property returns the block size used for training the model.
        '''
        return self.__block_size
    
    @property
    def max_iters(self: Self) -> int:
        '''
            This property returns the maximum number of iterations used for training the model.
        '''
        return self.__max_iters
    
    @property
    def eval_interval(self: Self) -> int:
        '''
            This property returns the evaluation interval used for training the model.
        '''
        return self.__eval_interval
    
    @property
    def learning_rate(self: Self) -> float:
        '''
            This property returns the learning rate used for training the model.
        '''
        return self.__learning_rate
    
    @property
    def eval_iters(self: Self) -> int:
        '''
            This property returns the evaluation iterations used for training the model.
        '''
        return self.__eval_iters
    
    @property
    def model(self: Self):
        '''
            This property returns the model.
        '''
        return self.__model

    def fit(self: Self, path_to_dataset: str|None=None, 
            train_test_split: float=0.8, *, 
            epochs: int=100, 
            verbose: bool=True) -> None:
        '''
            This method is responsible for training the model.
            It reads the dataset, captures the amount of unique words existent in the dataset, 
            creates the Transformers Model and trains it

            If the dataset was unchanged, it loads the model from the pickle file. If not, the training algorithm will be executed.

            Args:
                path_to_dataset (str): path to dataset used for training
        '''
        if path_to_dataset:
            self.__dataset = path_to_dataset

        if (pathlib.Path(__file__).parent.parent.parent.parent / 'model.pkl').exists():
            with open('model.pkl', 'rb') as f:
                self.__model = pickle.load(f)
        else:
            self.__train(epochs, verbose)

    def __serialize_model(self: Self) -> None:
        '''
            Serializes the model into a pickle file to avoid retraining it every time the chatbot is executed.
        '''

        with (pathlib.Path(__file__).parent.parent.parent.parent / 'model.pkl').open('wb') as f:
            pickle.dump(self.__model, f)

    def __train(self: Self, epochs: int, verbose: bool) -> None:
        '''
            Training algorithm of the Tranformers model
        '''

        with open(self.__dataset, 'r') as f:
            data = csv.reader(f)

        self.__model = Transformer(self.__device)

        for epoch in range(epochs):
            self.__model.train()
            ...
            self.__model.eval()
        if verbose: 
            print('\n',self.__model.parameters())
        
        self.__serialize_model()

    def predict(self: Self, message: str) -> str:
        '''
            This method is responsible for returning the answer of the model for the chatbot.
            It receives a message, tokenizes it, and passes it to the Transformers Model

            Args:
                message (str): message to be answered by the chatbot

        '''
        if not hasattr(self, '_Model__model'):
            raise UntrainedModelError("Model not trained yet. Use 'fit()' method to train it.")
        return 'self.__model.decode(message, trg)'

    __call__ = predict
    
    def check_db_change(self: Self, commit_on_change: bool=True) -> None:
        '''
            Verifies changes in the dataset. If there are changes, it will delete the serialized model.

            OBS: The changes are verified via git, so in order to properly verify the difference, commits will be made
            every time 
        '''
        out = subprocess.run(f'git diff {self.__dataset}/../approved.csv', shell=True, cwd=pathlib.Path(__file__).parent.parent.parent.parent.absolute(),
                       capture_output=True).stdout.strip()
        if out:
            subprocess.run(f'rm -f model.pkl', shell=True, cwd=pathlib.Path(__file__).parent.parent.parent.parent.absolute())
            self.__update_dataset()
            if commit_on_change:
                subprocess.run([f'git add .', 'git commit -am "Update dataset" --amend'], shell=True, cwd=pathlib.Path(__file__).parent.parent.parent.parent.absolute())

    def __update_dataset(self: Self) -> None: pass