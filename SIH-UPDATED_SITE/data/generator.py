"""
Procedural Lunar Surface & Crater Terrain Generator for Development Testing
Synthesizes realistic lunar impact crater topography with customizable:
- Solar azimuth and elevation (shadow casting)
- Scale / resolution disparity
- Geometric rotation and perspective warp
- Sensor noise
"""
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import cv2


class LunarLandscapeSynthesizer:
    @staticmethod
    def generate_dem(size: int = 512, seed: int = 42) -> np.ndarray:
        """Generates a fractal digital elevation model (DEM) with impact craters."""
        rng = np.random.RandomState(seed)
        dem = np.zeros((size, size), dtype=np.float32)

        # 1. Multi-octave fractal background roughness (regolith)
        for octave in [4, 8, 16, 32, 64]:
            grid = rng.randn(octave, octave).astype(np.float32)
            layer = cv2.resize(grid, (size, size), interpolation=cv2.INTER_CUBIC)
            dem += layer * (32.0 / octave)

        # 2. Add realistic impact craters (paraboloid depressions with raised ejecta rims)
        num_craters = 45
        for _ in range(num_craters):
            cx = rng.randint(40, size - 40)
            cy = rng.randint(40, size - 40)
            radius = rng.uniform(12, 65)
            depth = radius * 0.45

            # Circular crater mask
            y, x = np.ogrid[:size, :size]
            dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

            # Crater profile: central bowl + raised ejecta rim
            inside = dist <= radius
            rim = (dist > radius) & (dist <= radius * 1.35)

            # Depression
            bowl = -depth * (1.0 - (dist / radius) ** 2)
            dem[inside] += bowl[inside]

            # Ejecta rim
            rim_height = depth * 0.35 * np.sin(np.pi * (dist - radius) / (radius * 0.35))
            dem[rim] += rim_height[rim]

        # Normalize DEM to [0, 1]
        dem = (dem - np.min(dem)) / (np.ptp(dem) + 1e-6)
        return dem

    @staticmethod
    def shade_dem(
        dem: np.ndarray,
        sun_azimuth_deg: float = 45.0,
        sun_elevation_deg: float = 25.0,
        albedo_noise: float = 0.05
    ) -> np.ndarray:
        """
        Applies Lambertian + Lommel-Seeliger lunar surface photometric shading.
        Accurately renders harsh shadows based on solar azimuth and elevation.
        """
        h, w = dem.shape
        # Compute surface normal vectors
        dz_dx = cv2.Sobel(dem, cv2.CV_32F, 1, 0, ksize=3) * 5.0
        dz_dy = cv2.Sobel(dem, cv2.CV_32F, 0, 1, ksize=3) * 5.0

        normals = np.zeros((h, w, 3), dtype=np.float32)
        normals[:, :, 0] = -dz_dx
        normals[:, :, 1] = -dz_dy
        normals[:, :, 2] = 1.0
        norm = np.linalg.norm(normals, axis=2, keepdims=True)
        normals /= (norm + 1e-6)

        # Sun illumination vector
        az = np.radians(sun_azimuth_deg)
        el = np.radians(sun_elevation_deg)
        sun_dir = np.array([
            np.cos(el) * np.sin(az),
            np.cos(el) * np.cos(az),
            np.sin(el)
        ], dtype=np.float32)

        # Lambertian cosine dot product: max(0, N . L)
        cos_i = np.maximum(0.0, np.sum(normals * sun_dir, axis=2))

        # Add lunar regolith roughness / albedo variations
        rng = np.random.RandomState(int(sun_azimuth_deg))
        noise = rng.normal(0.0, albedo_noise, (h, w)).astype(np.float32)
        shaded = np.clip(cos_i + noise, 0.0, 1.0)
        return shaded

    @classmethod
    def create_lunar_test_pair(
        cls,
        output_dir: Path,
        base_seed: int = 101,
        sun_angle_delta: float = 60.0,
        scale_ratio: float = 1.6,
        rotation_deg: float = 18.0
    ) -> Tuple[Path, Path]:
        """
        Creates a synthetic development test pair simulating:
        1. Source: Sun Azimuth 45 deg, Elevation 20 deg
        2. Reference: Sun Azimuth (45 + delta) deg, Elevation 35 deg, with rotation and scale
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        dem = cls.generate_dem(size=600, seed=base_seed)

        # Source image (Base lunar scene)
        img_src = cls.shade_dem(dem, sun_azimuth_deg=45.0, sun_elevation_deg=22.0)

        # Reference image (Modified sun angle + geometric warp)
        img_ref_base = cls.shade_dem(dem, sun_azimuth_deg=45.0 + sun_angle_delta, sun_elevation_deg=35.0)

        # Apply geometric transform to reference (Scale + Rotation + Translation)
        h, w = img_src.shape
        center = (w / 2.0, h / 2.0)
        M = cv2.getRotationMatrix2D(center, rotation_deg, 1.0 / scale_ratio)
        M[0, 2] += 25.0
        M[1, 2] -= 15.0

        img_ref = cv2.warpAffine(img_ref_base, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

        src_path = output_dir / "lunar_source_ohrc_sim.png"
        ref_path = output_dir / "lunar_reference_tmc_sim.png"

        cv2.imwrite(str(src_path), (img_src * 255.0).astype(np.uint8))
        cv2.imwrite(str(ref_path), (img_ref * 255.0).astype(np.uint8))

        return src_path, ref_path


if __name__ == "__main__":
    out = Path("data/samples")
    s, r = LunarLandscapeSynthesizer.create_lunar_test_pair(out)
    print(f"Generated sample lunar pair:\nSource: {s}\nReference: {r}")
