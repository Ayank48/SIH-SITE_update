from typing import Tuple, List
"""
Lunar Illumination Normalization and Phase Congruency
Provides:
1. Phase Congruency / Local Energy Model (illumination-invariant feature maps)
2. Multi-Scale Retinex / Homomorphic Filtering (decouples reflectance from solar irradiance)
3. Symmetric Gradient Orientation (modulo pi, neutralizing 180-degree shadow flips)
4. CLAHE contrast normalization
"""
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter


class LunarIlluminationNormalizer:
    """Scientific algorithms for solar angle and illumination invariance on lunar terrain."""

    @staticmethod
    def apply_clahe(image: np.ndarray, clip_limit: float = 2.5, tile_grid_size: int = 8) -> np.ndarray:
        """
        Applies Contrast-Limited Adaptive Histogram Equalization.
        Expects float32 [0.0, 1.0], returns float32 [0.0, 1.0].
        """
        img_8u = np.clip(image * 255.0, 0, 255).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
        equalized = clahe.apply(img_8u)
        return equalized.astype(np.float32) / 255.0

    @staticmethod
    def multiscale_retinex(image: np.ndarray, sigmas=(15, 80, 250)) -> np.ndarray:
        """
        Multi-Scale Retinex (MSR) decomposition.
        Isolates high-frequency surface reflectance R(x,y) from low-frequency solar irradiance L(x,y):
        I(x,y) = R(x,y) * L(x,y) => log(R) = log(I) - log(L)
        """
        img_float = np.clip(image, 1e-4, 1.0)
        log_img = np.log(img_float)
        retinex = np.zeros_like(img_float)

        for sigma in sigmas:
            blur = gaussian_filter(img_float, sigma=sigma)
            blur = np.clip(blur, 1e-4, 1.0)
            retinex += (log_img - np.log(blur))

        retinex /= len(sigmas)
        # Normalize to [0.0, 1.0] using 2nd and 98th percentiles
        p2, p98 = np.percentile(retinex, (2, 98))
        if p98 > p2:
            retinex_norm = np.clip((retinex - p2) / (p98 - p2), 0.0, 1.0)
        else:
            retinex_norm = np.zeros_like(image)
        return retinex_norm

    @staticmethod
    def compute_phase_congruency(image: np.ndarray, nscales: int = 3, norient: int = 4) -> np.ndarray:
        """
        Simplified Fast 2D Phase Congruency approximation via directional Log-Gabor / Hilbert energy.
        Features occur where Fourier components are maximally in phase.
        Phase congruency is completely invariant to illumination brightness and contrast variations.
        """
        rows, cols = image.shape
        img_float = image.astype(np.float32)

        # High-pass filter in frequency domain
        f_transform = np.fft.fft2(img_float)
        f_shift = np.fft.fftshift(f_transform)

        y = np.linspace(-rows / 2, rows / 2, rows)
        x = np.linspace(-cols / 2, cols / 2, cols)
        X, Y = np.meshgrid(x, y)
        radius = np.sqrt(X ** 2 + Y ** 2) + 1e-5

        # Multi-scale bandpass filter bank
        total_energy = np.zeros((rows, cols), dtype=np.float32)
        total_amplitude = np.zeros((rows, cols), dtype=np.float32)

        center_wavelengths = [12.0 * (2.0 ** s) for s in range(nscales)]

        for w_0 in center_wavelengths:
            fo = 1.0 / w_0
            # Radial log-Gabor component
            r_filter = np.exp(-((np.log(radius / (rows * fo))) ** 2) / (2 * (np.log(0.65)) ** 2))
            r_filter[radius < 1.0] = 0

            # Filter response
            filtered_fft = f_shift * r_filter
            filtered_spatial = np.fft.ifft2(np.fft.ifftshift(filtered_fft))

            even = np.real(filtered_spatial)
            odd = np.imag(filtered_spatial)
            amplitude = np.sqrt(even ** 2 + odd ** 2) + 1e-6

            total_energy += amplitude
            total_amplitude += np.abs(even) + np.abs(odd)

        # Phase congruency = Energy / Amplitude sum
        epsilon = 0.01
        pc = total_energy / (total_amplitude + epsilon)
        pc = np.clip((pc - np.min(pc)) / (np.ptp(pc) + 1e-6), 0.0, 1.0)
        return pc.astype(np.float32)

    @staticmethod
    def compute_symmetric_gradients(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes gradient magnitude and orientation modulo pi.
        Mapping theta into [0, pi) guarantees that opposing shadows (180 deg flips)
        produce identical orientation representations.
        """
        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)

        magnitude = np.sqrt(gx ** 2 + gy ** 2)
        # Orientation in [-pi, pi]
        angle = np.arctan2(gy, gx)
        # Map into [0, pi)
        angle_sym = np.mod(angle, np.pi)

        # Normalize magnitude
        p98 = np.percentile(magnitude, 98)
        if p98 > 0:
            norm_mag = np.clip(magnitude / p98, 0.0, 1.0)
        else:
            norm_mag = magnitude

        return norm_mag.astype(np.float32), angle_sym.astype(np.float32)

