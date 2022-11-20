# DeepLabV3-Road-Boundary-Estimation

To run a file individually, download or copy that file, upload/paste in Google Colab, Kaggle or Jupyter Notebook. Update IMG_PATH, MASK_PATH, IMG_SUB_PATH, MASK_SUB_PATH, ONEHOT_MASK according to your file structure.

To use Combined_’models_with_loss_function_and_weight_options’ download or copy that file, upload/paste in Google Colab, Kaggle or Jupyter Notebook. 
  1. Select the model you want to use as backbone in  ‘model_name’
  2. Select the loss function you want to use for model training in ‘loss_fucntion’
  2. Select ‘Yes’ or ‘No’ depending on whether you want to handle class imbalance or not in ‘add_weight’
Then update IMG_PATH, MASK_PATH, IMG_SUB_PATH, MASK_SUB_PATH, ONEHOT_MASK according to your file structure.

If the folder structure of the dataset is like this:
D:.<br />
|---final dataset<br />
|&emsp;&emsp;|---mask<br />
|&emsp;&emsp;|&emsp;&emsp;|---mask<br />
|&emsp;&emsp;|---test Image<br />
|&emsp;&emsp;|---test one hot<br />
|&emsp;&emsp;|---train Image<br />
|&emsp;&emsp;|&emsp;&emsp;|---Image<br />
|&emsp;&emsp;|---train One hot<br />
|&emsp;&emsp;|&emsp;&emsp;|---train One hot<br />

Then the path veriables should be:
IMG_PATH = /final dataset/train Image/<br> 
MASK_PATH = /final dataset/mask/<br>
IMG_SUB_PATH = /final dataset/train Image/Image/&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;#training image<br> 
MASK_SUB_PATH = /final dataset/train One hot/One hot/&emsp;&emsp;&emsp;#Actually segment label<br> 
ONEHOT_MASK = /final dataset/mask/mask&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;#Here segmented label will be stored after preprocessing<br>


[This paper](https://ieeexplore.ieee.org/document/9521544) might be helpful for understanding this repository.

If you find this repository and paper helpful, we would appreciate using the following citations:

```
@article{das2021estimation,
  title={Estimation of road boundary for intelligent vehicles based on deepLabV3+ architecture},
  author={Das, Sunanda and Fime, Awal Ahmed and Siddique, Nazmul and Hashem, MMA},
  journal={IEEE Access},
  volume={9},
  pages={121060--121075},
  year={2021},
  publisher={IEEE}
}
```
