import React, { useState } from 'react';

interface SafeImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallbackSrc?: string;
  placeholderText?: string;
}

export const SafeImage: React.FC<SafeImageProps> = ({
  src,
  alt = 'Plant Image',
  fallbackSrc = '',
  placeholderText,
  className = '',
  ...props
}) => {
  const [hasError, setHasError] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  const handleError = () => {
    if (!hasError) {
      setHasError(true);
    }
  };

  const imageSource = hasError ? fallbackSrc : (src || fallbackSrc);

  return (
    <div className={`relative overflow-hidden bg-surface-container-high flex items-center justify-center ${className}`}>
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-surface-container-high animate-pulse">
          <span className="material-symbols-outlined text-outline-variant text-3xl">nature</span>
        </div>
      )}
      
      {(!hasError || fallbackSrc) ? (
        <img
          src={imageSource}
          alt={alt}
          onError={handleError}
          onLoad={() => setIsLoaded(true)}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            isLoaded || hasError ? 'opacity-100' : 'opacity-0'
          }`}
          {...props}
        />
      ) : (
        <div className="flex flex-col items-center justify-center text-outline-variant opacity-70">
          <span className="material-symbols-outlined text-4xl mb-2">hide_image</span>
          <span className="text-xs font-semibold uppercase tracking-widest">Không có ảnh minh họa</span>
        </div>
      )}

      {hasError && placeholderText && (
        <div className="absolute bottom-2 left-2 bg-black/60 px-2 py-0.5 rounded text-[10px] text-white">
          {placeholderText}
        </div>
      )}
    </div>
  );
};
