"""
Geometric mapping of finite elements from the reference coordinate
system to the global physical coordinate system.
"""

import scitools

class Mapping:
    pass

# this is more general than what it seems
class IsoparametricMapping(Mapping):
    def __init__(self, element):
        """
        Often a standard Element instance can be used to define
        mapping functions, e.g., ElmTriangle3n.
        """
        self.element = element

    def map(self, loc_pt, global_node_coor):
        # scalar version
        # vec version needs array of loc_pt and element set of global_elm_coor
        P = self.element.eval_N(loc_pt)
        C = global_node_coor
        return scitools_core.dot(P, C)

    def Jacobian(self, loc_pt, global_node_coor):
        M = self.element.eval_dN(loc_pt)
        C = global_node_coor
        J = scitools_core.dot(C, M)
        # make sure J is a matrix (1D: vector)
        if len(J.shape) == 1:  # 1D?
            J = J[:,scitools_core.NewAxis]
        return J
    
    def inverse_Jacobian(self, loc_pt, global_node_coor):
        J = self.Jacobian(loc_pt, global_node_coor)
        nsd = J.shape[0]
        #if nsd == 1:
        #    return
        Jinv = scitools_core.LinearAlgebra.inverse(J)
        return Jinv

    # vectorized versions: should implement in F77, array (e,i,j) of
    # J matrices, manual formulas for inverting each nsd*nsd block
    
    def _Jacobian_vec(self, loc_pt, coor, loc2glob, diagonal_Jacobian=False):
        """
        Vectorized implementation of Jacobian calculations.
        """
        # result: N(i,e), dN(i,j,e), detJ(e)
        # need: N, dN, detJ, elmcoor(i,j,e), dN_loc(i,j), J(i,j,e), invJ(i,j,e)
        # make C routine, this is quite straightforward
        # store dN(i,j,e) for field interpolation of gradients!

        # algorithms:
        # from coor and loc2glob to elmcoor(i,j,e)
        # for i, j, k, e:
        #     J(i,j,e) += N(k,j)*elmcoor(k,i,e)  (1st J=0)
        # if nsd==1:
        #    for e: invJ(1,1,e) = formula
        # if nsd==2:
        #    for e: invJ(1,1,e) = formula, invJ(1,2,e) = formula etc.
        #    take diagonal_Jacobian into account
        # same for nsd=3
        # need a special general loop for nsd>3 (can wait!)
        pass
    

def _test1D():
    coor = scitools_core.arr(data=[12, 20])
    from Element import ElmInterval2n
    elm = ElmInterval2n()
    m = IsoparametricMapping(elm)
    loc_pts = [-1, 0, 1, 0.5]
    for p in loc_pts:
        print '%s maps to %s' % (p, m.map(p,coor))
        print 'J:', m.Jacobian(p, coor)
        print 'J^{-1}:', m.inverse_Jacobian(p, coor)

def _tests():
    _test1D()
    
if __name__ == '__main__':
    _tests()
    
