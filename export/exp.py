import PyEmb

def save_as_exp(elements, filename, params):
    emb = PyEmb.Embroidery()

    for e in elements:
        for p in e.points(params['stitch_length'], params['stitch_distance']):
            ep = PyEmb.Point(2 * p[0] - 240, 240 - 2 * p[1])
            ep.color = 'Black'
            emb.addStitch(ep)

    emb.translate_to_origin()
    emb.scale(10.0 / params['pixels_per_millimeter'])
    with open(filename, "wb") as fp:
        fp.write(emb.export_melco(PyEmb.dbg))

