with unnested_products as (
  select 
    meals.client_id,
    meals.created_at,
    unnest(product_ids) AS product_id
    from meals
    where  product_ids is not null
    and client_id = {{client_id}}
    and created_at >= current_date - INTERVAL '30 day'
)
select 
  meals.client_id,
  meals.product_id,
  products.nombre,
  products.categoria,
  products.calorias,
  products.proteina,
  products.carbohidratos,
  count(meals.product_id) as count_products
from unnested_products as meals
left join products
on meals.product_id = products.id
group by 1,2,3,4,5,6,7
order by 8 desc