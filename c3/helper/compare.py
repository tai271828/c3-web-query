def cid_objs(cid_objs_base, cid_objs_target):
    flag = True
    for cid in cid_objs_base:
        try:
            # attributes
            attrs_base = cid_objs_base[cid]
            attrs_target = cid_objs_target[cid]
            for idx in range(len(attrs_base)):
                if not attrs_base[idx] == attrs_target[idx]:
                    flag = False
        except KeyError:
            print(cid)

    return flag