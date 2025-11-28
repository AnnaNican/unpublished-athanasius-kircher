
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { useState, useEffect } from 'react';
import { ArmillaryScene, PyramidScene } from './components/QuantumScene';
import { CelestialWheel, MonochordDiagram, SympathyChart } from './components/Diagrams';
import { ArrowDown, Menu, X, Scroll, Feather, Compass } from 'lucide-react';

const AuthorityCard = ({ name, role, delay }: { name: string, role: string, delay: string }) => {
  return (
    <div className="flex flex-col group animate-fade-in-up items-center p-8 bg-[#FDFBF7] rounded-sm border border-stone-300 shadow-sm hover:shadow-xl hover:border-nobel-gold transition-all duration-500 w-full max-w-xs" style={{ animationDelay: delay }}>
      <div className="w-16 h-16 rounded-full bg-stone-100 border-2 border-nobel-gold/30 mb-4 flex items-center justify-center text-nobel-gold font-display text-2xl font-bold">
        {name.charAt(0)}
      </div>
      <h3 className="font-display text-xl text-nobel-ink text-center mb-2 tracking-wide">{name}</h3>
      <div className="w-8 h-px bg-nobel-gold mb-3 opacity-60"></div>
      <p className="text-xs text-stone-500 font-serif italic text-center leading-relaxed">{role}</p>
    </div>
  );
};

const App: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    setMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      const headerOffset = 100;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth"
      });
    }
  };

  return (
    <div className="min-h-screen bg-[#F9F8F4] text-nobel-ink selection:bg-nobel-gold selection:text-white overflow-x-hidden">
      
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 border-b ${scrolled ? 'bg-[#F9F8F4]/95 backdrop-blur-sm border-stone-200 py-3 shadow-sm' : 'bg-transparent border-transparent py-6'}`}>
        <div className="container mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center gap-4 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-10 h-10 border-2 border-nobel-gold rounded-full flex items-center justify-center text-nobel-gold font-display font-bold text-xl pb-1 hover:bg-nobel-gold hover:text-white transition-colors">
              <Compass size={20} />
            </div>
            <div className={`flex flex-col transition-opacity duration-300 ${scrolled ? 'opacity-100' : 'opacity-0 md:opacity-100'}`}>
              <span className="font-display font-bold text-lg tracking-widest text-nobel-ink">SAPIENTIA</span>
              <span className="font-serif text-[10px] text-stone-500 uppercase tracking-[0.2em]">MDCXLIV</span>
            </div>
          </div>
          
          <div className="hidden md:flex items-center gap-8 text-xs font-bold tracking-[0.15em] text-stone-600">
            <a href="#prologue" onClick={scrollToSection('prologue')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Prologue</a>
            <a href="#sympathy" onClick={scrollToSection('sympathy')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Sympathia</a>
            <a href="#harmony" onClick={scrollToSection('harmony')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Harmonia</a>
            <a href="#authorities" onClick={scrollToSection('authorities')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Auctoritas</a>
          </div>

          <button className="md:hidden text-stone-900 p-2" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="fixed inset-0 z-40 bg-[#F9F8F4] flex flex-col items-center justify-center gap-8 text-xl font-display animate-fade-in text-stone-800">
            <a href="#prologue" onClick={scrollToSection('prologue')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Prologue</a>
            <a href="#sympathy" onClick={scrollToSection('sympathy')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Sympathia</a>
            <a href="#harmony" onClick={scrollToSection('harmony')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Harmonia</a>
            <a href="#authorities" onClick={scrollToSection('authorities')} className="hover:text-nobel-gold transition-colors cursor-pointer uppercase">Auctoritas</a>
        </div>
      )}

      {/* Hero Section */}
      <header className="relative h-screen flex items-center justify-center overflow-hidden border-b border-stone-200">
        <ArmillaryScene />
        
        {/* Vignette Overlay */}
        <div className="absolute inset-0 z-0 pointer-events-none bg-[radial-gradient(circle_at_center,rgba(249,248,244,0.5)_0%,rgba(249,248,244,0.8)_60%,rgba(245,244,240,1)_100%)]" />

        <div className="relative z-10 container mx-auto px-6 text-center mt-12">
          <div className="inline-flex items-center justify-center gap-3 mb-6 opacity-70">
            <div className="h-px w-12 bg-nobel-gold"></div>
            <div className="text-nobel-gold text-xs tracking-[0.3em] uppercase font-display font-bold">Athanasius Kircher</div>
            <div className="h-px w-12 bg-nobel-gold"></div>
          </div>
          
          <h1 className="font-display text-4xl md:text-6xl lg:text-8xl font-medium leading-tight mb-6 text-nobel-ink drop-shadow-sm">
            DE HIEROGLYPHICIS
          </h1>
          <p className="font-serif italic text-xl md:text-3xl text-stone-600 mb-10 max-w-4xl mx-auto leading-relaxed">
            Sapientiae Fontibus et Eorum ad Caelestem Harmoniam Correspondentia
          </p>
          
          <div className="flex justify-center">
             <a href="#prologue" onClick={scrollToSection('prologue')} className="group flex flex-col items-center gap-3 text-xs font-bold tracking-widest text-stone-400 hover:text-nobel-gold transition-colors cursor-pointer">
                <span>INCIPIAMUS</span>
                <span className="p-3 border border-stone-300 rounded-full group-hover:border-nobel-gold transition-colors bg-white/40 backdrop-blur-sm">
                    <ArrowDown size={14} />
                </span>
             </a>
          </div>
        </div>
      </header>

      <main>
        {/* Prologue */}
        <section id="prologue" className="py-32 bg-white relative">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-24 bg-gradient-to-b from-transparent to-stone-300"></div>
          
          <div className="container mx-auto px-6 md:px-12 grid grid-cols-1 md:grid-cols-12 gap-16 items-start">
            <div className="md:col-span-5 sticky top-32">
              <div className="inline-block mb-4 text-xs font-bold tracking-[0.2em] text-nobel-gold uppercase font-display">Liber I: The Mystery</div>
              <h2 className="font-display text-4xl mb-8 leading-tight text-nobel-ink">The Hidden Architectonic Structure</h2>
              <p className="text-stone-500 font-serif italic mb-8">
                "Those venerable custodians of primordial wisdom did conceal beneath the enigmatic veil of their hieroglyphic characters..."
              </p>
              <div className="w-24 h-1 bg-nobel-gold/30"></div>
            </div>
            
            <div className="md:col-span-7 text-lg md:text-xl text-stone-700 leading-relaxed space-y-8 font-serif">
              <p>
                <span className="drop-cap">I</span>n undertaking this most sacred investigation into the profound mysteries which the ancient Egyptian priests, those venerable custodians of primordial wisdom, did conceal beneath the enigmatic veil of their hieroglyphic characters, I find myself compelled to address first that fundamental question which has perplexed scholars from the time of Herodotus.
              </p>
              <p>
                Through painstaking examination of no fewer than forty-seven obelisks and seventeen papyri of undoubted antiquity, I demonstrate that these sacred symbols do contain within their seemingly simple forms the entire architectonic structure of both terrestrial and celestial knowledge.
              </p>
              <p>
                 Do these symbols participate in that divine emanation whereby the Supreme Architect did impress upon creation the immutable laws governing the revolution of the spheres and the mathematical progressions underlying musical consonance? That such participation is demonstrably certain, I shall endeavor to prove.
              </p>
            </div>
          </div>
        </section>

        {/* Interactive: Celestial Wheel */}
        <section id="sympathy" className="py-32 bg-[#F5F4F0] border-y border-stone-200">
            <div className="container mx-auto px-6">
                <div className="max-w-4xl mx-auto text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-4 py-1 border border-stone-300 text-stone-600 text-xs font-bold tracking-[0.2em] uppercase rounded-full mb-6 bg-white">
                        <Feather size={12}/> Sympathia Hieroglyphica
                    </div>
                    <h2 className="font-display text-4xl md:text-5xl mb-6 text-nobel-ink">The Solar Disk & Planetary Motion</h2>
                    <p className="text-lg text-stone-600 leading-relaxed font-serif">
                       The ancient hierophants understood that each character functions as a living symbol which participates ontologically in the reality it represents. Align the celestial bodies to reveal the hidden concordances.
                    </p>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                    <div className="order-2 lg:order-1">
                       <CelestialWheel />
                    </div>
                    <div className="order-1 lg:order-2 space-y-6">
                        <div className="p-8 bg-white border border-stone-200 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-4 opacity-10">
                                <Compass size={100} />
                            </div>
                            <h3 className="font-display text-2xl text-nobel-ink mb-4">Magnetic Declination</h3>
                            <p className="text-stone-600 mb-4 leading-relaxed font-serif">
                                Recent discoveries in the science of magnetism, conducted within the laboratories of the Roman College, confirm the existence of invisible sympathies binding all orders of creation.
                            </p>
                            <p className="text-stone-600 leading-relaxed font-serif">
                                The winged solar disk corresponds with mathematical precision to proportional relationships governing planetary motions, adjusted for magnetic declinations found near iron ore deposits.
                            </p>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-stone-500 font-serif italic">
                            <span className="w-8 h-px bg-stone-400"></span>
                            <span>Observation of the Eclipse of 1654</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        {/* Musurgia Universalis */}
        <section id="harmony" className="py-32 bg-[#1C1917] text-stone-200 overflow-hidden relative">
            <div className="absolute inset-0 z-0">
                <div className="absolute top-0 left-0 w-full h-full opacity-20 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]"></div>
                <div className="absolute w-[500px] h-[500px] bg-nobel-gold/10 rounded-full blur-[100px] top-[-100px] right-[-100px]"></div>
            </div>

            <div className="container mx-auto px-6 relative z-10">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
                     <div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-stone-800 text-nobel-gold text-xs font-bold tracking-widest uppercase rounded-sm mb-6 border border-stone-700">
                           Musurgia Universalis
                        </div>
                        <h2 className="font-display text-4xl md:text-5xl mb-8 text-white">The Geometry of Sound</h2>
                        <p className="text-lg text-stone-400 mb-6 leading-relaxed font-serif">
                            Certain combinations of tones, when produced according to Pythagorean ratios, possess the power to influence not only the human soul but also the behavior of mineral substances.
                        </p>
                        <p className="text-lg text-stone-400 leading-relaxed font-serif mb-8">
                            My extensive experiments demonstrate that these patterns correspond remarkably to the geometric forms inscribed upon the walls of the Great Pyramid.
                        </p>
                        
                        <MonochordDiagram />
                     </div>
                     <div className="relative h-[600px] w-full rounded-sm overflow-hidden border border-stone-800 bg-black/50">
                        <PyramidScene />
                        <div className="absolute bottom-6 left-0 right-0 text-center text-xs text-stone-500 font-display tracking-widest uppercase">
                            Fig. IV: The Great Pyramid as Resonator
                        </div>
                     </div>
                </div>
            </div>
        </section>

        {/* Correspondence Chart */}
        <section className="py-32 bg-[#F9F8F4]">
            <div className="container mx-auto px-6">
                <div className="max-w-3xl mx-auto text-center mb-16">
                    <h2 className="font-display text-4xl md:text-5xl mb-6 text-nobel-ink">The Tetrakyts & The Cosmos</h2>
                    <p className="text-lg text-stone-600 leading-relaxed font-serif">
                        Coptic manuscripts reveal that hieroglyphic placement follows a sophisticated system of numerical correspondences based upon the sacred tetraktys.
                    </p>
                </div>
                <div className="max-w-4xl mx-auto">
                    <SympathyChart />
                </div>
            </div>
        </section>

        {/* Coda & Authorities */}
        <section id="authorities" className="py-32 bg-white border-t border-stone-200">
           <div className="container mx-auto px-6">
                <div className="flex flex-col md:flex-row gap-16">
                    <div className="md:w-1/3">
                        <div className="sticky top-32">
                            <div className="inline-block mb-4 text-xs font-bold tracking-widest text-nobel-gold uppercase font-display">Coda Philosophica</div>
                            <h2 className="font-display text-3xl mb-6 text-nobel-ink">The Supreme Hieroglyph</h2>
                            <p className="text-stone-600 font-serif leading-relaxed mb-6">
                                Thus do we perceive that the hieroglyphic symbols serve as luminous bridges spanning the apparent chasm between mind and matter.
                            </p>
                            <p className="text-stone-600 font-serif leading-relaxed italic">
                                "Nature herself is the supreme hieroglyph, each creature serving as a living symbol through which the Creator speaks."
                            </p>
                        </div>
                    </div>
                    
                    <div className="md:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-8">
                         <div className="col-span-full mb-8 text-center md:text-left">
                            <h3 className="font-display text-2xl text-stone-800 mb-2">Venerable Authorities</h3>
                            <p className="text-stone-500 font-serif italic text-sm">Cited in this investigation</p>
                         </div>
                        <AuthorityCard 
                            name="Hermes Trismegistus" 
                            role="Priscus Theologiae" 
                            delay="0s" 
                        />
                        <AuthorityCard 
                            name="Pythagoras" 
                            role="Numerus Mensura Rerum" 
                            delay="0.1s" 
                        />
                        <AuthorityCard 
                            name="Plotinus" 
                            role="Enneads" 
                            delay="0.2s" 
                        />
                        <AuthorityCard 
                            name="Iamblichus" 
                            role="De Mysteriis" 
                            delay="0.3s" 
                        />
                        <AuthorityCard 
                            name="Father Schott" 
                            role="Societas Jesu" 
                            delay="0.4s" 
                        />
                        <AuthorityCard 
                            name="Tycho Brahe" 
                            role="Astronomiae Instauratae" 
                            delay="0.5s" 
                        />
                    </div>
                </div>
           </div>
        </section>

      </main>

      <footer className="bg-[#1a1a1a] text-stone-400 py-24 border-t border-stone-800">
        <div className="container mx-auto px-6 flex flex-col items-center text-center gap-8">
            <div className="mb-4">
                <Compass size={48} className="text-nobel-gold opacity-80" />
            </div>
            <div>
                <div className="text-white font-display font-bold text-3xl mb-4 tracking-widest">DE HIEROGLYPHICIS</div>
                <p className="text-sm font-serif italic max-w-lg mx-auto leading-relaxed opacity-70">
                    A digital restoration of the treatise on the Hieroglyphic Sources of Wisdom and Their Correspondence to Celestial Harmony.
                </p>
            </div>
            <div className="w-12 h-px bg-stone-700 my-4"></div>
            <div className="text-xs tracking-[0.2em] uppercase text-stone-600">
                MDCXLIV • Romae • Collegium Romanum
            </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
