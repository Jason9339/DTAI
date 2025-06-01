# Create model directory if it doesn't exist
mkdir model

# Change to model directory
cd model

# Download and rename the model files

# Convnext model
echo "下載 ConvNeXt 模型..."
wget -O convnext_90.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/Efu2Ymy6sPtErzeij1LrwJ0BnGeWPz-wQj2StVvXwsyldQ?download=1'

# densenet model
echo "下載 DenseNet 模型..."
wget -O densenet_86.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/EcQoDmAFFjNKjj92_mnVca8B6xjfQb_3yz-Vw_ALyyt5gA?download=1'

# resnet model
echo "下載 ResNet 模型..."
wget -O resnet50_78.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/Edw9hsi3A8lPtZqVUSlo_cEBwjPH22Dopw4URRVYSo5WLg?download=1'

# vit model
echo "下載 ViT 模型..."
wget -O vit_model_74.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/EXcNR_cTrP5Ci9B2vJQCwpYBxgppkfBQQQVr7_FE23UMoQ?download=1'

# swin model
echo "下載 Swin Transformer 模型..."
wget -O swin_model_94.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/EakjxJYOmoZMt30Y_c8buTABm1L91B9AawFR1WQSmiTJGg?download=1'

# swinv2 model (注意：原始連結中有拼寫錯誤，已修正)
echo "下載 SwinV2 Transformer 模型..."
wget -O swinv2_model_94.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/EdIcKZ79utxFq_wDNWnp9BIBfAfcsv_-b6Ucs7zSe-iF0w?download=1'

# efficientnet model
wget -O efficientnet_84.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/EXzbadlYwDFHlbChnFATNiAB6DG2srzmqVn3hV5ETs5QIQ?download=1'

# vgg model
wget -O vgg_model_78.pth 'https://mail3nccu-my.sharepoint.com/:u:/g/personal/111703037_mail3_nccu_tw/Ef2A-cxdpw1Jm8Y7JrVEocMBZHQeKIW6wZbcDVC8pTlQDw?download=1'

echo "所有模型下載完成！"
echo "模型檔案列表："
ls -la *.pth

# Return to the previous directory
cd ..
