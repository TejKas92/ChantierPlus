import React, { useRef, useState, useEffect } from 'react';
import SignatureCanvas from 'react-signature-canvas';

interface SignaturePadProps {
    onEnd: (dataUrl: string) => void;
    disabled?: boolean;
    signatureData?: string;
}

const SignaturePad: React.FC<SignaturePadProps> = ({ onEnd, disabled = false, signatureData = '' }) => {
    const sigCanvas = useRef<SignatureCanvas>(null);
    const [isEmpty, setIsEmpty] = useState(true);
    const [lastSignatureData, setLastSignatureData] = useState(signatureData);

    // Clear canvas when signatureData is cleared from parent
    useEffect(() => {
        // If signature data went from filled to empty
        if (lastSignatureData && !signatureData && sigCanvas.current) {
            console.log('Clearing signature canvas');
            sigCanvas.current.clear();
            setIsEmpty(true);
        }
        setLastSignatureData(signatureData);
    }, [signatureData, lastSignatureData]);

    const clear = () => {
        sigCanvas.current?.clear();
        setIsEmpty(true);
        onEnd('');
    };

    const handleEnd = () => {
        if (sigCanvas.current) {
            setIsEmpty(sigCanvas.current.isEmpty());
            if (!sigCanvas.current.isEmpty()) {
                try {
                    // Try with getTrimmedCanvas first
                    onEnd(sigCanvas.current.getTrimmedCanvas().toDataURL('image/png'));
                } catch (error) {
                    // Fallback to regular toDataURL if getTrimmedCanvas fails
                    console.warn('getTrimmedCanvas failed, using toDataURL:', error);
                    onEnd(sigCanvas.current.toDataURL('image/png'));
                }
            }
        }
    };

    return (
        <div className={`border border-slate-300 rounded-lg p-2 ${disabled ? 'bg-slate-100 opacity-60' : 'bg-white'} relative`}>
            {disabled && (
                <div className="absolute inset-0 bg-slate-200 bg-opacity-50 rounded-lg flex items-center justify-center z-10">
                    <p className="text-sm text-slate-600 font-medium">Veuillez remplir tous les champs requis ci-dessus</p>
                </div>
            )}
            <SignatureCanvas
                ref={sigCanvas}
                penColor="black"
                canvasProps={{
                    width: 300,
                    height: 150,
                    className: `sigCanvas w-full h-40 ${disabled ? 'bg-slate-100' : 'bg-slate-50'}`
                }}
                onEnd={handleEnd}
            />
            <div className="mt-2 flex justify-end">
                <button
                    type="button"
                    onClick={clear}
                    disabled={disabled}
                    className="text-sm text-red-500 hover:text-red-700 underline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Effacer
                </button>
            </div>
        </div>
    );
};

export default SignaturePad;
