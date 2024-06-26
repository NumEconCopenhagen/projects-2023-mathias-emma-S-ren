from scipy import optimize
import sympy as sm
import numpy as np
import matplotlib.pyplot as plt
from types import SimpleNamespace

# Funcion that derives the equations for the nullclines
def analytical(latex = False):
    """ Derives the equations for the nullclines based on the transition equations for human and physical capital
    Args: 
    None
    
    Returns:
    Nullclines for physical and human capital h(k)
    if latex = true, printes the latex code for the nulclines
    """

    # 1. Defining the variables as symbols for using sympy
    k = sm.symbols('k')
    h = sm.symbols('h')
    sh = sm.symbols('s_h')
    sk = sm.symbols('s_k')
    delta = sm.symbols('delta')
    phi = sm.symbols('phi')
    alpha = sm.symbols('alpha')
    g = sm.symbols('g')
    n = sm.symbols('n')

    # 2. Function for deriving the analytical solution
    #Transition lines:
    k_t2 = (sk*k**alpha*h**phi+(1-delta)*k)/((1+n)*(1+g))
    h_t2 = (sh*k**alpha*h**phi+(1-delta)*h)/((1+n)*(1+g))

    #Change in capital stock () - Sollow equations 
    delta_k = k_t2 - k 
    delta_h = h_t2 - h

    #Nultlines (Stock of capital is constant)
    sollow_k = sm.Eq(delta_k,0)
    sollow_h = sm.Eq(delta_h,0)

    #Isolating k, and h in each equation - For drawing the phase diagram h should be isolated in both
    nult_k = sm.solve(sollow_k,h)
    nult_h = sm.solve(sollow_h,h)

    out = {}
    out['sollow_k'] = sollow_k
    out['sollow_h'] = sollow_h

    out['nult_k'] = nult_k
    out['nult_h'] = nult_h

    out['nult_k_eq'] = sm.Eq( h, out['nult_k'][0])
    out['nult_h_eq'] = sm.Eq( h, out['nult_h'][0])


    if latex == True: 

        print(f'  Latex code for the nult line for physical capital: \n {sm.latex(nult_k)} \n\n')
        print(f'  Latex code for the nult line for human capital: \n  {sm.latex(nult_h)}')

    return out


# Define a function for the transition equations 
def f(h,k,s_h,s_k,g,n,alpha,phi,delta):
    """input arguments:
    h     (float): Human capital per effective worker (Stock)
    k     (float): Physical capital per effective worker (Stock)
    s_h   (float): Savings/Investments in human capital
    s_k   (float): Savings/Investments in physical capital
    g     (float): Growth rate of technology
    n     (float): Growth rate of labour force
    alpha (float): Return on physical capital
    phi   (float): Return on human capital
    delta (float): Depreciation rate of physical capital
    
    Returns: 
    The transition equation for human and physical capital per effective worker in steady state
    """

    h_function = 1/((1+n)*(1+g))*(s_h*k**(alpha)*h**(phi)+(1-delta)*h)-h
    k_function = 1/((1+n)*(1+g))*(s_k*k**(alpha)*h**(phi)+(1-delta)*k)-k
    
    return h_function,k_function



# Setting up baseline parameters in a SimpleNamespace
par = SimpleNamespace(**{'s_h':0.13, 's_k':0.25, 'g':0.016, 'n':0.014, 'alpha':1/3, 'phi':1/3, 'delta':0.02, 'tau':0.1, 'eta':0.05})


# Defining a function to calculate the nullclines
def solve_ss(s_h=par.s_h, s_k=par.s_k, g=par.g, n=par.n, alpha=par.alpha, phi=par.phi, delta=par.delta):
    """args:
    s_h    (float): Savings/Investments in human capital
    s_k    (float): Savings/Investments in physical capital
    g      (float): Growth rate of technology
    n      (float): Growth rate of labour force
    alpha  (float): Return on physical capital
    phi    (float): Return on human capital
    delta  (float): Depreciation rate
    
    Returns:
    The nullclines for physical and human capital
    """
    # 1. Setting up the grids
    # Grids for physical capital
    k_vec = np.linspace(0.01, 100, 1000)

    # Grid for human capital when physical capital per effective worker is constant
    h_vec_DeltaK0 = np.empty(1000)

    # Grid for human capital when human capital per effective worker is constant
    h_vec_DeltaH0 = np.empty(1000)

    # 2. Finding the nullclines
    for i, k in enumerate(k_vec):
        # Solve for constant human capital per effective worker
        obj = lambda h: f(h, k, s_h, s_k, g, n, alpha, phi, delta)[0]
        result = optimize.root_scalar(obj, method='brentq', bracket=[1e-20, 100])
        h_vec_DeltaH0[i] = result.root

        # Solve for constant physical capital per effective worker
        obj = lambda h: f(h, k, s_h, s_k, g, n, alpha, phi, delta)[1]
        result = optimize.root_scalar(obj, method='brentq', bracket=[1e-20, 100])
        h_vec_DeltaK0[i] = result.root

    # 3. Creating the plot
    fig = plt.figure(figsize=(13,5))
    ax = fig.add_subplot(1,2,1)
    ax.plot(k_vec, h_vec_DeltaK0, label=r'$\Delta \tilde{k}=0$')
    ax.plot(k_vec, h_vec_DeltaH0, label=r'$\Delta \tilde{h}=0$')
    ax.set_xlabel(r'Physical capital per effective worker, $\tilde{k}$')
    ax.set_ylabel(r'Human capital per effective worker, $\tilde{h}$')
    ax.set(xlim=(0, 100), ylim=(0, 100))
    ax.set_title('Phase diagram')

    # 4. Setting up the objective and solving the model. We repeat this step instead of just calling it, so it will update when changing parameters with the widgets, i.e. moving the SS-mark.
    objective = lambda x: [f(x[0],x[1],s_h,s_k,g,n,alpha,phi,delta)]
    solution = optimize.root(objective,[1,1],method = 'broyden1')
    num_solution = solution.x
    
    # 5. Draw lines and mark the point of the ss-value. It is interactive, so it will change, when chainging the parameters
    plt.axvline(num_solution[1], ymax=1, color='gray', linestyle='--') 
    plt.axhline(num_solution[0], xmax=1, color='gray', linestyle='--') 
    ax.scatter(num_solution[1],num_solution[0],color='black',s=80,zorder=2.5, label=r'$\Delta\tilde{h}=\Delta\tilde{k}=0$')
    ax.legend() 
    
    # 6. Print the steady state values
    print(f'The level of human and physical capital per effective worker in steady \n state with updated parameters are = {num_solution[0]:.3f} and {num_solution[1]:.3f}, respectively.')


# Define a function to simulate the Solow model
def solow_model(s_h=par.s_h, s_k=par.s_k, g=par.g, n=par.n, alpha=par.alpha, phi=par.phi, delta=par.delta, tau=par.tau, eta=par.eta):
    # 1. Set initial values
    k = 1               # Capital stock per effective worker
    l = 1               # Labour per effective worker
    a = 1               # Technology level
    h = 1               # Human capital per effective worker
    
    # 2. Create empty arrays to store data
    num_periods = 1000
    k_array = np.empty(num_periods)
    y_array = np.empty(num_periods)
    h_array = np.empty(num_periods)
    
    # 3. Simulate the model for 1,000 periods
    for t in range(num_periods):
        k_array[t] = k
        y_array[t] = k ** alpha * h ** phi 
        h_array[t] = h
        
        # Calculate investment
        i_k = s_k * y_array[t] * (1 - tau)
        i_h = s_h * y_array[t] * (1 + eta)
        
        # Update capital and human capital
        k = 1/((1+n)*(1+g))*((1 - delta) * k + i_k) / (l * a)
        h = 1/((1+n)*(1+g))*((1 - delta) * h + i_h) / (l * a)
        
    # 4. Plot the results
    t_values = np.arange(num_periods)
    plt.plot(t_values, k_array, label='Physical capital per effective worker')
    plt.plot(t_values, y_array, label='Output per effective worker')
    plt.plot(t_values, h_array, label='Human capital per effective worker')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Level')
    plt.ylim(0, 70)
    plt.title('Simulation of the Solow model with human capital and tax for 1,000 periods')
    if eta>tau: print('OBS: The tax on physical capital is lower than the subsidy on human capital. This is not a stable equilibrium.')
    plt.show()
    