import cv2
def is_blurr(image,threshold=50.0):
    gray=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    laplacian_var=cv2.Laplacian(gray,cv2.CV_64F).var()
    return laplacian_var<threshold