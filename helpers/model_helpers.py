from os.path import join

from direct.particles.ParticleEffect import ParticleEffect

# load_model will assume that the model is under
# /assets/models/<name>/<name>.obj
def load_model(name):
    model = loader.loadModel(join("assets","models",name, name+".obj"))
    return model


def load_particles(name):
   p = ParticleEffect()
   p.loadConfig(join("assets","particles",name, "{}.ptf".format(name)))
   return p
