from typing import Iterable, Tuple, Union, Literal, Sequence, Dict

import numpy as np
import pandas as pd
from anndata import AnnData
from anndata._core.raw import Raw


# TODO: allow sequences: ("obsm", "X_pca", [0, 1])
AnnDataPath = Union[
    Tuple[Literal["X"], str],  # TODO: Support this or do ("layer", None, str)?
    Tuple[Literal["layer"], str, str],
    Tuple[Literal["obs"], str],
    Tuple[Literal["obsm"], str, Union[int, str]],
    Tuple[Literal["obsp"], str, Literal[0, 1]],  # TODO: actually needs one more parameter (cell name)
    Tuple[Literal["raw"], Literal["X"], str],  # TODO: or "raw/X" and "raw/obs"?
    Tuple[Literal["raw"], Literal["obs"], str],
]


def obs_df(
    adata: AnnData,
    paths: Iterable[Union[str, AnnDataPath]] = (),
    *,
    gene_symbols: AnnDataPath = None,
    # no use_raw, no layer.
) -> pd.DataFrame:
    paths = list(map(normalize_adpath, paths))
    names = paths_to_names(paths)
    columns = {n: get_obs_vector(adata, p, gene_symbols) for n, p in names.items()}
    return pd.DataFrame(columns, adata.obs_names)


def get_obs_vector(adata: Union[AnnData, Raw], path: Union[str, AnnDataPath], gene_symbols: Union[str, AnnDataPath]):
    path = normalize_adpath(path)
    gene_symbols = None if gene_symbols is None else normalize_adpath(gene_symbols)
    
    if path[0] == "layer":  # X is here after normalizing
        layer = adata.X if path[1] == "X" else adata.layers[path[1]]
        idx = adata.var_names if gene_symbols is None else adata.var[gene_symbols]
        # TODO: can layers also be data frames and have to be handled as obsm?
        return layer[:, idx == path[2]]
    if path[0] == "obs":
        return adata.obs[path[1]]
    assert not isinstance(adata, Raw)
    if path[0] == "obsm":
        m = adata.obsm[path[1]]
        return m[path[2]] if isinstance(m, pd.DataFrame) else m[:, path[2]]
    if path[0] == "obsp":
        raise NotImplementedError("No good idea how to specify this. 'obsp/neighbors/CellName/1 vs .../2?'")
    if path[0] == "raw":
        return get_obs_vector(adata.raw, path[1:], gene_symbols)
    else:
        raise ValueError(f"Unknown AnnData attribute {path[0]!r} in path {path!r}")


SHORT_CODES = dict(
    X=["layer", "X"],
    l=["layer"],
    o=["obs"],
    m=["obsm"],
    p=["obsp"],
    rX=["raw", "X"],
    ro=["raw", "obs"],
)


def normalize_adpath(path: Union[str, AnnDataPath]) -> AnnDataPath:
    # path is shorthand: "obs/Foo" and "o/Foo"
    if not isinstance(path, str):
        return path
    path = path.split("/")
    path[:1] = SHORT_CODES.get(path[0], [path[0]])
    if path[0] in {"obsm", "obsp"}:
        # TODO: how to normalize
        try:
            path[-1] = int(path[-1])
        except ValueError:
            pass
    return tuple(path)


def paths_to_names(paths: Sequence[AnnDataPath], length: int = 1) -> Dict[str, AnnDataPath]:
    names = {}
    dupes = {}
    for path, name in zip(paths, (path_name(p, length) for p in paths)):
        dupes.setdefault(name, []).append(path)
    for name, paths_dup in dupes.items():
        if len(paths_dup) == 1:
            names[name] = paths_dup[0]
        elif any(len(p) > length for p in paths_dup):
            names.update(paths_to_names(paths_dup, length + 1))
        else:
            raise ValueError(f"Not sure how {name} can be extended for {paths_dup}")
    return names


def path_name(path: AnnDataPath, length: int = 1) -> str:
    if length == 1 and path[0] == "obsp":
        return path[-2]  # just key
    if length in {1, 2} and path[0] == "obsm":
        if isinstance(path[-1], int):
            return f"{path[-2]}{path[-1]+1}"  # X_pca1
        else:  # normal
            return path[-1] if length == 1 else f"{path[-2]}-{path[-1]}"
    if length <= 2:
        return "-".join(path[-length:])
    return f"{path[:-2]}{path_name(path, length=2)}"
    
    


def old():
    ad = adata.raw if use_raw else adata
    idx = ad.var_names if gene_symbols is None else ad.var[gene_symbols]
    gene_names = pd.Series(ad.var_names, index=idx)
    del ad, idx

    lookup_keys = []
    not_found = []
    found_twice = []
    for key in keys:
        in_obs, in_var_index = False, False
        if key in adata.obs.columns:
            lookup_keys.append(key)
            in_obs = True
        if key in gene_names.index:
            in_var_index = True
            if not in_obs:
                lookup_keys.append(gene_names[key])
        # Test failure cases
        if not (in_obs or in_var_index):
            not_found.append(key)
        elif in_obs and in_var_index:
            found_twice.append(key)
    if len(not_found) > 0 or len(found_twice) > 0:
        ad_str = "adata.raw" if use_raw else "adata"
        if gene_symbols is None:
            gene_error = f"`{ad_str}.var_names`"
        else:
            gene_error = f"gene_symbols column `{ad_str}.var['{gene_symbols}']`"
        if len(found_twice) > 0:
            raise KeyError(
                f"Found keys {found_twice} in columns of `obs` and in {gene_error}."
            )
        else:
            raise KeyError(
                f"Could not find keys '{not_found}' in columns of `adata.obs` or in"
                f" {gene_error}."
            )

    # Make df
    df = pd.DataFrame(index=adata.obs_names)
    for k, l in zip(keys, lookup_keys):
        if not use_raw or k in adata.obs.columns:
            df[k] = adata.obs_vector(l, layer=layer)
        else:
            df[k] = adata.raw.obs_vector(l)
    for k, idx in obsm_keys:
        added_k = f"{k}-{idx}"
        val = adata.obsm[k]
        if isinstance(val, np.ndarray):
            df[added_k] = np.ravel(val[:, idx])
        elif isinstance(val, spmatrix):
            df[added_k] = np.ravel(val[:, idx].toarray())
        elif isinstance(val, pd.DataFrame):
            df[added_k] = val.loc[:, idx]
    return df
