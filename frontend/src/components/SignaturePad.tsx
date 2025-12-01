import React, { useRef, useState } from 'react';
import SignatureCanvas from 'react-signature-canvas';

interface SignaturePadProps {
    onEnd: (dataUrl: string) => void;
}

const SignaturePad: React.FC<SignaturePadProps> = ({ onEnd }) => {
    const sigCanvas = useRef<SignatureCanvas>(null);
    const [isEmpty, setIsEmpty] = useState(true);

    const clear = () => {
        sigCanvas.current?.clear();
        setIsEmpty(true);
        onEnd('');
    };

    const handleEnd = () => {
        if (sigCanvas.current) {
            setIsEmpty(sigCanvas.current.isEmpty());
            if (!sigCanvas.current.isEmpty()) {
                onEnd(sigCanvas.current.getTrimmedCanvas().toDataURL('image/png'));
            }
        }
    };

    return (
        <div className="border border-slate-300 rounded-lg p-2 bg-white">
            <SignatureCanvas
                ref={sigCanvas}
                penColor="black"
                canvasProps={{ width: 300, height: 150, className: 'sigCanvas w-full h-40 bg-slate-50' }}
                onEnd={handleEnd}
            />
            <div className="mt-2 flex justify-end">
                <button
                    type="button"
                    onClick={clear}
                    className="text-sm text-red-500 hover:text-red-700 underline"
                >
                    Effacer
                </button>
            </div>
        </div>
    );
};

export default SignaturePad;
