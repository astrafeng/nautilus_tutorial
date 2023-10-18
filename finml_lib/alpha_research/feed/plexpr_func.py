import polars as pl 

def rank_pct(expr: pl.Expr) -> pl.Expr:
    """
    Calculate the rank percent of a series.

    Parameters
    ----------
    expr : pl.Expr
        The series to calculate the rank percent of.

    Returns
    -------
    pl.Expr
        The rank percent of the series.
    """
    return expr.rank() / (expr.len() - expr.null_count())

def slope(x:pl.Expr, y: pl.Expr) -> pl.Expr:
    """
    Calculate the slope of a linear regression line between x and y.

    Parameters
    ----------
    x : pl.Expr
        The x values of the linear regression line.
    y : pl.Expr
        The y values of the linear regression line.

    Returns
    -------
    pl.Expr
        The slope of the linear regression line.
    """
    return (pl.corr(x, y) * pl.std(y)) / pl.std(x)

def rsqure(x:pl.Expr, y: pl.Expr) -> pl.Expr:
    """
    Calculate the R^2 value of a linear regression line between x and y.

    Parameters
    ----------
    x : pl.Expr
        The x values of the linear regression line.
    y : pl.Expr
        The y values of the linear regression line.

    Returns
    -------
    pl.Expr
        The R^2 value of the linear regression line.
    """
    return pl.pow(pl.corr(x, y), 2)

def residual(x:pl.Expr, y: pl.Expr) -> pl.Expr:
    """
    Calculate the residuals of a linear regression line between x and y.

    Parameters
    ----------
    x : pl.Expr
        The x values of the linear regression line.
    y : pl.Expr
        The y values of the linear regression line.

    Returns
    -------
    pl.Expr
        The residuals of the linear regression line.
    """
    return y - (pl.corr(x, y) * (y / x) * x)