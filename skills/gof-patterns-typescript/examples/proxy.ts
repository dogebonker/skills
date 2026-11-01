export {};

// Proxy: same interface as the real service, adds lazy loading and caching in front of it.
interface ImageService {
  load(path: string): string;
}

class DiskImageService implements ImageService {
  load(path: string): string {
    console.log(`reading ${path} from disk`);
    return `pixels(${path})`;
  }
}

class CachingImageProxy implements ImageService {
  #real?: DiskImageService;
  readonly #cache = new Map<string, string>();

  load(path: string): string {
    const hit = this.#cache.get(path);
    if (hit !== undefined) return hit;
    this.#real ??= new DiskImageService();
    const data = this.#real.load(path);
    this.#cache.set(path, data);
    return data;
  }
}

const images: ImageService = new CachingImageProxy();
console.log(images.load("logo.png"));
console.log(images.load("logo.png"));
