import { expect, it } from 'vitest';
import { rankPointerIndex } from '../../src/features/requests/Requests';
const svg=(x:number,y=0)=>({getScreenCTM:()=>({inverse:()=>({})}),createSVGPoint:()=>({x:0,y:0,matrixTransform:()=>({x,y})})}) as unknown as SVGSVGElement;
it('uses transformed user-space coordinates for first middle last and clamps',()=>{
 expect(rankPointerIndex(svg(51),361,100,29)).toBe(0);
 expect(rankPointerIndex(svg(51+333*14/29),500,100,29)).toBe(14);
 expect(rankPointerIndex(svg(384),700,100,29)).toBe(29);
 expect(rankPointerIndex(svg(-100),0,0,29)).toBe(0);
 expect(rankPointerIndex(svg(600),0,0,29)).toBe(29);
});
it('ignores missing screen transform',()=>expect(rankPointerIndex({getScreenCTM:()=>null} as unknown as SVGSVGElement,0,0,29)).toBeNull());
it('ignores singular or unavailable transform',()=>expect(rankPointerIndex({getScreenCTM:()=>({inverse:()=>{throw Error('singular');}}),createSVGPoint:()=>({})} as unknown as SVGSVGElement,0,0,29)).toBeNull());
it('ignores nonfinite points and handles empty/single point',()=>{
 expect(rankPointerIndex(svg(NaN),0,0,29)).toBeNull();expect(rankPointerIndex(svg(51,Infinity),0,0,29)).toBeNull();
 expect(rankPointerIndex(svg(51),0,0,-1)).toBeNull();expect(rankPointerIndex(svg(384),0,0,0)).toBe(0);
});
