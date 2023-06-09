"""
face alignment implementation from https://github.com/1adrianb/face-alignment/issues/165
"""
import numpy as np, face_alignment
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from skimage import io
import collections, cv2

def umeyama(src, dst, estimate_scale):
    """
    From DeepFace lab: 
    https://github.com/iperov/DeepFaceLab/blob/master/core/mathlib/umeyama.py
    
    Estimate N-D similarity transformation with or without scaling.
    Parameters
    ----------
    src : (M, N) array
        Source coordinates.
    dst : (M, N) array
        Destination coordinates.
    estimate_scale : bool
        Whether to estimate scaling factor.
    Returns
    -------
    T : (N + 1, N + 1)
        The homogeneous similarity transformation matrix. The matrix contains
        NaN values only if the problem is not well-conditioned.
    References
    ----------
    .. [1] "Least-squares estimation of transformation parameters between two
            point patterns", Shinji Umeyama, PAMI 1991, DOI: 10.1109/34.88573
    """
    num = src.shape[0]
    dim = src.shape[1]
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)
    src_demean = src - src_mean
    dst_demean = dst - dst_mean
    A = np.dot(dst_demean.T, src_demean) / num
    d = np.ones((dim,), dtype=(np.double))
    if np.linalg.det(A) < 0:
        d[dim - 1] = -1
    else:
        T = np.eye((dim + 1), dtype=(np.double))
        U, S, V = np.linalg.svd(A)
        rank = np.linalg.matrix_rank(A)
        if rank == 0:
            return np.nan * T
            if rank == dim - 1:
                if np.linalg.det(U) * np.linalg.det(V) > 0:
                    T[:dim, :dim] = np.dot(U, V)
                else:
                    s = d[dim - 1]
                    d[dim - 1] = -1
                    T[:dim, :dim] = np.dot(U, np.dot(np.diag(d), V))
                    d[dim - 1] = s
            else:
                T[:dim, :dim] = np.dot(U, np.dot(np.diag(d), V))
            if estimate_scale:
                scale = 1.0 / src_demean.var(axis=0).sum() * np.dot(S, d)
        else:
            scale = 1.0
    T[:dim, dim] = dst_mean - scale * np.dot(T[:dim, :dim], src_mean.T)
    T[:dim, :dim] *= scale
    return T


def transform_points(points, mat, invert=False):
    if invert:
        mat = np.linalg.inv(mat)
    ones = np.zeros(points.shape[0])
    points = np.column_stack((points, ones))
    points = (mat @ points.T).T
    points = points[:, :3]
    return points


def align(facepoints):
    landmarks_68_3D = np.array([
     [
      -73.393523, -29.801432, 47.667532],
     [
      -72.775014, -10.949766, 45.909403],
     [
      -70.533638, 7.929818, 44.84258],
     [
      -66.850058, 26.07428, 43.141114],
     [
      -59.790187, 42.56439, 38.635298],
     [
      -48.368973, 56.48108, 30.750622],
     [
      -34.121101, 67.246992, 18.456453],
     [
      -17.875411, 75.056892, 3.609035],
     [
      0.098749, 77.061286, -0.881698],
     [
      17.477031, 74.758448, 5.181201],
     [
      32.648966, 66.929021, 19.176563],
     [
      46.372358, 56.311389, 30.77057],
     [
      57.34348, 42.419126, 37.628629],
     [
      64.388482, 25.45588, 40.886309],
     [
      68.212038, 6.990805, 42.281449],
     [
      70.486405, -11.666193, 44.142567],
     [
      71.375822, -30.365191, 47.140426],
     [
      -61.119406, -49.361602, 14.254422],
     [
      -51.287588, -58.769795, 7.268147],
     [
      -37.8048, -61.996155, 0.442051],
     [
      -24.022754, -61.033399, -6.606501],
     [
      -11.635713, -56.686759, -11.967398],
     [
      12.056636, -57.391033, -12.051204],
     [
      25.106256, -61.902186, -7.315098],
     [
      38.338588, -62.777713, -1.022953],
     [
      51.191007, -59.302347, 5.349435],
     [
      60.053851, -50.190255, 11.615746],
     [
      0.65394, -42.19379, -13.380835],
     [
      0.804809, -30.993721, -21.150853],
     [
      0.992204, -19.944596, -29.284036],
     [
      1.226783, -8.414541, -36.94806],
     [
      -14.772472, 2.598255, -20.132003],
     [
      -7.180239, 4.751589, -23.536684],
     [
      0.55592, 6.5629, -25.944448],
     [
      8.272499, 4.661005, -23.695741],
     [
      15.214351, 2.643046, -20.858157],
     [
      -46.04729, -37.471411, 7.037989],
     [
      -37.674688, -42.73051, 3.021217],
     [
      -27.883856, -42.711517, 1.353629],
     [
      -19.648268, -36.754742, -0.111088],
     [
      -28.272965, -35.134493, -0.147273],
     [
      -38.082418, -34.919043, 1.476612],
     [
      19.265868, -37.032306, -0.665746],
     [
      27.894191, -43.342445, 0.24766],
     [
      37.437529, -43.110822, 1.696435],
     [
      45.170805, -38.086515, 4.894163],
     [
      38.196454, -35.532024, 0.282961],
     [
      28.764989, -35.484289, -1.172675],
     [
      -28.916267, 28.612716, -2.24031],
     [
      -17.533194, 22.172187, -15.934335],
     [
      -6.68459, 19.029051, -22.611355],
     [
      0.381001, 20.721118, -23.748437],
     [
      8.375443, 19.03546, -22.721995],
     [
      18.876618, 22.394109, -15.610679],
     [
      28.794412, 28.079924, -3.217393],
     [
      19.057574, 36.298248, -14.987997],
     [
      8.956375, 39.634575, -22.554245],
     [
      0.381549, 40.395647, -23.591626],
     [
      -7.428895, 39.836405, -22.406106],
     [
      -18.160634, 36.677899, -15.121907],
     [
      -24.37749, 28.677771, -4.785684],
     [
      -6.897633, 25.475976, -20.893742],
     [
      0.340663, 26.014269, -22.220479],
     [
      8.444722, 25.326198, -21.02552],
     [
      24.474473, 28.323008, -5.712776],
     [
      8.449166, 30.596216, -20.671489],
     [
      0.205322, 31.408738, -21.90367],
     [
      -7.198266, 30.844876, -20.328022]],
      dtype=(np.float32))
    pts2 = np.float32(((0, 0), (160, 0), (160, 160)))
    centered_face = facepoints - facepoints.mean(axis=0)
    landmarks_68_3D = landmarks_68_3D
    mat = umeyama(centered_face, landmarks_68_3D, True)
    transformed_face = transform_points(centered_face, mat, False)
    return transformed_face