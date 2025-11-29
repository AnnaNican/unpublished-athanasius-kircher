
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RotateCcw, Star, Music, Move, Info } from 'lucide-react';

// --- CELESTIAL WHEEL DIAGRAM ---
// A simplified interactive Volvelle
export const CelestialWheel: React.FC = () => {
  const [rotationInner, setRotationInner] = useState(0);
  const [rotationOuter, setRotationOuter] = useState(0);
  const [aligned, setAligned] = useState(false);

  // Check alignment (simplified: if difference is multiple of 360 approx)
  useEffect(() => {
    const diff = Math.abs((rotationOuter - rotationInner) % 360);
    // Target alignment: when relative rotation is close to 0 (or specific angle)
    // Let's say alignment happens when they are 180 degrees apart relative to initial
    const isAligned = (diff > 170 && diff < 190); 
    setAligned(isAligned);
  }, [rotationInner, rotationOuter]);

  const rotate = (setter: React.Dispatch<React.SetStateAction<number>>, val: number) => {
    setter(prev => prev + val);
  }

  return (
    <div className="flex flex-col items-center p-8 bg-white rounded-sm shadow-xl border border-stone-200 my-8 relative overflow-hidden">
      {/* Parchment texture overlay */}
      <div className="absolute inset-0 opacity-10 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/cream-paper.png')]"></div>

      <h3 className="font-display text-xl mb-2 text-nobel-ink z-10">Volvelle of Correspondences</h3>
      <p className="text-sm text-stone-500 mb-8 text-center max-w-md font-serif italic z-10">
        Rotate the disks to align the Planetary Signs with the Hieroglyphic Emanations.
      </p>
      
      <div className="relative w-80 h-80 flex items-center justify-center select-none">
         {/* Static Base: The Zodiac or Fixed Stars */}
         <div className="absolute w-full h-full rounded-full border border-stone-300 flex items-center justify-center bg-[#FDFBF7]">
            {[...Array(12)].map((_, i) => (
                <div key={i} className="absolute text-[8px] font-serif text-stone-400" style={{ transform: `rotate(${i * 30}deg) translateY(-150px)` }}>
                    {['ARIES', 'TAVR', 'GEMI', 'CANC', 'LEO', 'VIRG', 'LIBR', 'SCOR', 'SAGI', 'CAPR', 'AQUA', 'PISC'][i]}
                </div>
            ))}
         </div>

         {/* Outer Ring: Planets (Interactable) */}
         <motion.div 
            className="absolute w-64 h-64 rounded-full border-2 border-stone-400 flex items-center justify-center shadow-md cursor-grab active:cursor-grabbing bg-[#F9F8F4]"
            animate={{ rotate: rotationOuter }}
            transition={{ type: "spring", stiffness: 50, damping: 20 }}
            drag="x" // Simplified interaction: drag left/right rotates
            dragConstraints={{ left: 0, right: 0 }}
            onDrag={(e, info) => rotate(setRotationOuter, info.delta.x)}
         >
            <div className="absolute w-full h-full border border-stone-300 rounded-full opacity-50"></div>
            {[...Array(7)].map((_, i) => (
                <div key={i} className="absolute text-lg font-serif text-nobel-ink font-bold" style={{ transform: `rotate(${i * (360/7)}deg) translateY(-110px)` }}>
                    {['☉', '☽', '☿', '♀', '♂', '♃', '♄'][i]}
                </div>
            ))}
            <div className="absolute top-2 text-[8px] uppercase tracking-widest text-stone-400">Orbis Planetarum</div>
         </motion.div>

         {/* Inner Ring: Hieroglyphs (Interactable) */}
         <motion.div 
            className="absolute w-40 h-40 rounded-full border-2 border-nobel-gold flex items-center justify-center shadow-sm cursor-grab active:cursor-grabbing bg-white"
            animate={{ rotate: rotationInner }}
            transition={{ type: "spring", stiffness: 50, damping: 20 }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            onDrag={(e, info) => rotate(setRotationInner, info.delta.x)}
         >
            <div className="absolute w-full h-full border border-stone-200 rounded-full opacity-50"></div>
            {[...Array(4)].map((_, i) => (
                <div key={i} className="absolute text-xl font-display text-nobel-gold" style={{ transform: `rotate(${i * 90}deg) translateY(-60px)` }}>
                    {['𓀀', '𓃻', '𓆣', '𓁹'][i]}
                </div>
            ))}
             <div className="absolute top-2 text-[8px] uppercase tracking-widest text-nobel-gold">Sympathia</div>
         </motion.div>

         {/* Center Pin */}
         <div className="absolute w-4 h-4 rounded-full bg-nobel-gold border-2 border-white shadow-sm z-20"></div>
      </div>

      <div className={`mt-8 px-6 py-2 transition-all duration-700 font-serif text-sm border-t border-b ${aligned ? 'border-nobel-gold text-nobel-ink bg-nobel-gold/10' : 'border-transparent text-transparent'}`}>
         "Harmonia Caelestis Confirmed"
      </div>
      
      <div className="mt-4 text-[10px] text-stone-400 uppercase tracking-widest flex items-center gap-2">
         <Move size={12}/> Drag rings to rotate
      </div>
    </div>
  );
};

// --- MONOCHORD DIAGRAM ---
// A visualization of frequency/ratio
export const MonochordDiagram: React.FC = () => {
    const [position, setPosition] = useState(50); // 0 to 100
    
    // Calculate ratio based on position (simplified)
    const ratio = position > 0 ? (100 / position).toFixed(2) : "∞";
    
    // Determine if it's a "sacred" ratio (approximate)
    const isSacred = [50, 33, 66, 25, 75].some(v => Math.abs(v - position) < 2);

    return (
        <div className="bg-stone-900 border border-stone-700 p-8 rounded-sm shadow-2xl max-w-md mx-auto relative overflow-hidden">
            <h3 className="font-display text-lg text-nobel-gold mb-4 border-b border-stone-800 pb-2">The Divine Monochord</h3>
            
            {/* String Visualization */}
            <div className="relative h-24 flex items-center my-6">
                {/* The String */}
                <div className="absolute left-0 right-0 h-0.5 bg-stone-500"></div>
                <div 
                    className={`absolute left-0 h-0.5 transition-colors duration-200 ${isSacred ? 'bg-nobel-gold shadow-[0_0_10px_#C5A059]' : 'bg-stone-400'}`} 
                    style={{ width: `${position}%` }}
                ></div>
                
                {/* The Bridge (Slider) */}
                <input 
                    type="range" 
                    min="10" 
                    max="90" 
                    value={position} 
                    onChange={(e) => setPosition(parseInt(e.target.value))}
                    className="absolute w-full z-20 opacity-0 cursor-ew-resize h-full"
                />
                <div 
                    className="absolute w-1 h-8 bg-white rounded-sm z-10 pointer-events-none transform -translate-y-1/2 top-1/2 flex flex-col items-center justify-between py-1"
                    style={{ left: `${position}%` }}
                >
                    <div className="w-4 h-4 border-l border-t border-white transform rotate-45 -mt-3 bg-stone-900"></div>
                </div>

                {/* Nodes */}
                <div className="absolute left-0 w-2 h-2 bg-stone-500 rounded-full"></div>
                <div className="absolute right-0 w-2 h-2 bg-stone-500 rounded-full"></div>
                <div className="absolute left-1/2 w-1 h-1 bg-stone-700 rounded-full top-1/2 -mt-0.5"></div>
                <div className="absolute left-1/3 w-1 h-1 bg-stone-700 rounded-full top-1/2 -mt-0.5"></div>
                <div className="absolute left-2/3 w-1 h-1 bg-stone-700 rounded-full top-1/2 -mt-0.5"></div>
            </div>

            <div className="flex justify-between items-end font-serif text-stone-400 text-sm">
                <div>
                    <div className="text-[10px] uppercase tracking-widest text-stone-600">Length</div>
                    <div className="text-xl text-white">{position}%</div>
                </div>
                <div className="text-center">
                    <div className={`transition-all duration-300 ${isSacred ? 'opacity-100 scale-110 text-nobel-gold' : 'opacity-0 scale-90'}`}>
                        <Star size={16} fill="#C5A059" />
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-[10px] uppercase tracking-widest text-stone-600">Ratio</div>
                    <div className="text-xl text-white">1 : {parseFloat(ratio).toFixed(1)}</div>
                </div>
            </div>
            
            <p className="mt-6 text-xs text-stone-500 font-serif italic text-center">
                ADJUST THE BRIDGE TO DISCOVER THE CONSONANCES
            </p>
        </div>
    );
}

// --- SYMPATHY CHART ---
// Stylized Bar Chart
export const SympathyChart: React.FC = () => {
    // Data representing "strength of sympathy"
    const materials = [
        { name: "Ferrum (Iron)", val: 85, color: "#78716C" },
        { name: "Magnes (Loadstone)", val: 100, color: "#C5A059" },
        { name: "Anima (Soul)", val: 95, color: "#A8A29E" },
        { name: "Plumbum (Lead)", val: 20, color: "#44403C" },
    ];

    return (
        <div className="flex flex-col gap-6 p-8 bg-white border border-stone-200 shadow-sm relative">
             <div className="absolute top-2 right-2 text-stone-300">
                <Info size={16} />
             </div>
             <h3 className="font-display text-xl text-nobel-ink text-center mb-4">Tabula Sympathiae</h3>
             
             <div className="space-y-6">
                {materials.map((m, idx) => (
                    <div key={idx} className="group">
                        <div className="flex justify-between text-sm font-serif text-stone-600 mb-2">
                            <span>{m.name}</span>
                            <span className="font-mono text-xs opacity-50">{m.val}</span>
                        </div>
                        <div className="h-1 w-full bg-stone-100 relative overflow-hidden">
                            {/* Background lines for ruler effect */}
                            <div className="absolute inset-0 bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAYAAACp8Z5+AAAAIklEQVQIW2NkQAKrVq36zwjjgzjwqgAAOYAOyAAzwAhiQAAAAABJRU5ErkJggg==')] opacity-20"></div>
                            
                            <motion.div 
                                className="h-full relative"
                                style={{ backgroundColor: m.color }}
                                initial={{ width: 0 }}
                                whileInView={{ width: `${m.val}%` }}
                                transition={{ duration: 1.5, ease: "easeOut", delay: idx * 0.2 }}
                            >
                                <div className="absolute right-0 top-0 bottom-0 w-px bg-white/50"></div>
                            </motion.div>
                        </div>
                    </div>
                ))}
             </div>
             
             <div className="mt-4 border-t border-stone-100 pt-4 text-center">
                <p className="text-[10px] text-stone-400 uppercase tracking-widest font-serif">
                    Measured at Collegium Romanum, Anno 1654
                </p>
             </div>
        </div>
    )
}
