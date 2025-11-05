# Roman Numeral Recognition Challenge: Data-Centric Approach

## 📖 Storyline
As a data scientist at the Ancient Numerals Research Institute, you've been tasked with improving their handwritten Roman numeral recognition system. The current model performs poorly due to data quality issues. Your team has spent months developing a sophisticated neural network architecture, but the results are still unsatisfactory.
The lead researcher believes the problem isn't with the model but with the training data itself. She's challenging you to prove this hypothesis by taking a data-centric approach to solving the problem without modifying the model architecture.

## 🎯 Objective
Your task is to improve the accuracy of a Roman numeral recognition model by focusing exclusively on data quality improvements. You must clean the provided dataset, remove problematic samples, balance class distributions, and potentially augment the data—all without modifying the model architecture or hyperparameters in `train.py`. 

**Important:** Your goal is to improve the training and validation data only.

## 🚩 FLAG
For this task, there is no flag. Solve the task and you will be rewarded.

## 📂 Dataset
- A collection of handwritten Roman numeral images (I, II, III, IV, V, VI, VII, VIII, IX, X)
- Dataset is organized in directories:
  - `data/train/` - Training images (you can modify these)
  - `data/val/` - Validation images (you can modify these)

## 📋 Project Structure
You are provided with the [following files](https://drive.google.com/drive/folders/1LVXMW6Y9ID54zgVEpKfRsIphZL6zKnAi?usp=sharing):
```
data/
  ├── train/                # Directory containing training images
  └── val/           # Directory containing validation images

train.py                    # Script to train the model (DO NOT MODIFY)
convert.py                  # Script to convert images if needed    
requirements.txt            # List of required Python packages
setup.ps1                   # PowerShell script to set up environment (Windows)
setup.sh                    # Shell script to set up environment (macOS/Linux)
```

## 🚀 Getting Started

### 1. Run the Setup Script

Choose the appropriate script for your operating system:

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

> ⏱️ **Note:** Installation may take 1-5 minutes. Please be patient while dependencies are downloaded and installed.

### 2. Activate the Virtual Environment

After setup completes, activate your virtual environment:

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Prepare and Clean the Dataset

Focus on improving the quality of the training data:
- Examine the dataset for outliers in each class
- Look for mislabeled or problematic samples
- Consider data augmentation techniques (rotations, zooms, brightness adjustments)
- Balance class distributions if needed

If you want to use your own data, the `convert.py` script may be helpful for converting your images to the correct format.

### 4. Train the Model

Run the training script to train the model on your cleaned dataset:

**Windows:**
```powershell
python .\train.py
```

**Linux/macOS:**
```bash
python train.py
```

The training script will:
- Train the model using your prepared data
- Save the best model weights to `best_model.weights.h5`

If the desired accuracy is not achieved, iterate on your data preprocessing until you reach **>90% validation accuracy**.

### 5. Submit Your Model Weights

Once you achieve satisfactory validation accuracy, submit your trained model weights file (`best_model.weights.h5`). 

The evaluation system will:
- Load your model weights
- Evaluate on a private test set
- Return your accuracy score and pass/fail status
- Reveal the flag if you achieve >90% accuracy

## ✅ Expected Output

Your submission should be a **model weights file** (`best_model.weights.h5`) that:
1. Achieves >90% accuracy on the test set (70 points)
2. Achieves >93% accuracy for bonus points (+30 points, 100 total)
3. Generalizes well to unseen data

When your model achieves the target accuracy, the flag will be revealed.

## 🏆 Scoring Criteria

- **< 90% accuracy:** 0 points
- **90% accuracy:** 70 points (base score)
- **90-93% accuracy:** 70-100 points (proportional)
- **≥ 93% accuracy:** 100 points (70 base + 30 bonus)
- **Hint penalties:** Points are deducted for taking hints